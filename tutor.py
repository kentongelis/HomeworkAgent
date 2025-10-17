from dotenv import load_dotenv
from typing import List, Dict, Any
from langchain.text_splitter import MarkdownTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
import json


class MarkdownTutor:
    def __init__(self, markdown_text, name):
        load_dotenv()
        self.name = name
        splitter = MarkdownTextSplitter(chunk_size=800, chunk_overlap=100)
        docs = splitter.create_documents([markdown_text])
        embeddings = OpenAIEmbeddings()
        self.vs = Chroma.from_documents(docs, embeddings)

        self.retriever = self.vs.as_retriever(
            search_type="similarity", search_kwargs={"k": 6}
        )

        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4)

        retrieval_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful assistant that reformulates user questions for document retrieval.",
                ),
                (
                    "human",
                    "Chat history: {chat_history}\nUser question: {input}\nRewrite this question for searching relevant documents:",
                ),
            ]
        )

        self.history_aware_retriever = create_history_aware_retriever(
            llm=self.llm, retriever=self.retriever, prompt=retrieval_prompt
        )

        system_prompt = """You are a helpful and knowledgeable tutor. 
            Use the provided context to answer the student's question clearly and in detail.
            If the answer is not in the context, say so honestly."""

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "Context:\n{context}\n\nQuestion:\n{input}"),
            ]
        )

        combine_chain = create_stuff_documents_chain(self.llm, prompt)
        self.rag_chain = create_retrieval_chain(
            retriever=self.history_aware_retriever, combine_docs_chain=combine_chain
        )

        self.chat_history: List[tuple[str, str]] = []
        self.quiz: Dict[str, Any] = {"questions": [], "current": 0, "score": 0}

    def ask(self, question):
        """Answer a student's question using RAG (Retrieval-Augmented Generation)."""
        inputs = {"input": question, "chat_history": self.chat_history}

        # Run retrieval + generation chain
        out = self.rag_chain.invoke(inputs)

        # Handle both output formats (depending on LangChain version)
        answer = out.get("answer") or out.get("output_text", "") or str(out)

        # Track conversation history
        self.chat_history.append((question, answer))

        return answer

    def generate_quiz(self, num_questions=5, multiple_choice=True):
        """Generate a quiz specifically from this tutor's own lesson content."""

        quiz_prompt = f"""
        IMPORTANT: If the correct answers or options include HTML or CSS code or tags, 
        show them literally (e.g., <h1>, <p>, <header>, display: flex) — do NOT escape, hide, or remove them.

        The lesson content below is specific to the topic "{self.name}".
        Use only this content to generate the quiz questions.

        Based on this lesson's content, generate {num_questions} quiz questions.
        {"Make them multiple choice with 4 options (A–D)" if multiple_choice else "Make them short-answer questions."}
        Provide answers in strict JSON format as a list of objects with keys:
        'question', {'options' if multiple_choice else ''}, and 'answer'.
        Example for multiple choice:
        [
            {{
                "question": "What does HTML stand for?",
                "options": [
                    "Hyper Trainer Marking Language",
                    "Hyper Text Markup Language",
                    "Home Tool Markup Language",
                    "Hyperlinks and Text Markup Language"
                ],
                "answer": "Hyper Text Markup Language"
            }}
        ]
        """

        # ✅ Instead of a static retrieval query, use this tutor’s own stored documents
        docs = self.retriever.get_relevant_documents(f"Core concepts of {self.name}")
        context = "\n".join([f"```markdown\n{d.page_content}\n```" for d in docs])

        full_prompt = f"Context:\n{context}\n\n{quiz_prompt}"

        response = self.llm.invoke(full_prompt).content

        try:
            quiz_data = json.loads(response)
        except json.JSONDecodeError:
            # try to recover if JSON is malformed
            fixed_json = response[response.find("[") : response.rfind("]") + 1]
            quiz_data = json.loads(fixed_json)

        self.quiz = {
            "questions": quiz_data,
            "current": 0,
            "score": 0,
        }
        return quiz_data

    def ask_quiz_question(self):
        """Ask the next question in the current quiz"""
        if not self.quiz["questions"]:
            return "No quiz generated yet. Use generate_quiz() first."

        if self.quiz["current"] >= len(self.quiz["questions"]):
            total = len(self.quiz["questions"])
            score = self.quiz["score"]
            percent = round((score / total) * 100)
            self.quiz = {
                "questions": [],
                "current": 0,
                "score": 0,
            }  # Reset for next time
            return f"🎉 You've completed the quiz!\nYour final score: {score}/{total} ({percent}%)"

        q = self.quiz["questions"][self.quiz["current"]]
        question_text = f"Q{self.quiz['current'] + 1}. {q['question']}"
        if "options" in q:
            question_text += "\n" + "\n".join(
                [f"{chr(65+i)}. {opt}" for i, opt in enumerate(q["options"])]
            )
        return question_text

    def answer_quiz(self, user_answer):
        """Check the user's answer and update score"""
        if not self.quiz["questions"]:
            return "No active quiz. Use generate_quiz() first."

        if self.quiz["current"] >= len(self.quiz["questions"]):
            return "Quiz already finished. Generate a new one!"

        q = self.quiz["questions"][self.quiz["current"]]
        correct = q["answer"].strip().lower()

        # Handle multiple choice
        if "options" in q:
            opts = [opt.lower() for opt in q["options"]]
            if user_answer.strip().upper() in ["A", "B", "C", "D"]:
                index = ord(user_answer.upper()) - 65
                user_answer = q["options"][index]
            user_correct = user_answer.strip().lower() == correct
        else:
            # Fuzzy check with LLM
            check_prompt = f"Question: {q['question']}\nCorrect answer: {correct}\nUser answer: {user_answer}\nIs the user's answer correct? Reply only 'Yes' or 'No'."
            verdict = self.llm.invoke(check_prompt).content.strip().lower()
            user_correct = "yes" in verdict

        if user_correct:
            self.quiz["score"] += 1
            feedback = "✅ Correct!"
        else:
            feedback = f"❌ Incorrect. The correct answer was: {q['answer']}."

        self.quiz["current"] += 1
        if self.quiz["current"] >= len(self.quiz["questions"]):
            total = len(self.quiz["questions"])
            score = self.quiz["score"]
            percent = round((score / total) * 100)
            feedback += (
                f"\n\n🎓 Quiz complete! Final score: {score}/{total} ({percent}%)"
            )
            self.quiz = {"questions": [], "current": 0, "score": 0}

        return feedback
