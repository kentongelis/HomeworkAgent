from dotenv import load_dotenv
from typing import List
from langchain.text_splitter import MarkdownTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


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

        self.llm = ChatOpenAI(model="gpt-4o-mini")

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

    def ask(self, question):
        inputs = {"input": question, "chat_history": self.chat_history}
        out = self.rag_chain.invoke(inputs)
        answer = out.get("answer") or out.get("output_text", "")
        self.chat_history.append((question, answer))
        return answer


lesson1_md = """===== 01-Semantic-HTML.md =====
# FEW 1.1 - Semantic HTML

➡️ [**Slides**](https://docs.google.com/presentation/d/1N4lM8Iwa5VEeeCLw-5QyJgsUkyMakVOLWw8Nx-DGrGI/edit?usp=sharing)

<!-- > -->

## Warmup

Breakout into groups of 4: 

- share your name and where you are from
- Why you wanted to join the ACS dept.
- What questions do you have about how to make websites? Get creative? We’ll be sure to address your questions during this class!  

<!--Instructor Tip: post the last question in the class slack channel and have students share their answers on a threaded message.-->

<!-- > -->

## Learning Objectives <!--(2 min)-->

- Describe semantic HTML
- Use Semantic HTML
- Write HTML with correct syntax
- Markup content and preserve context and meaning

<!-- > -->

### What are Learning Objectives? 

Learning objectives are the concepts and ideas that you need to know to claim mastery of a subject.

Learning Objectives are often skills that are related to success at job interviews and on the job.

<!-- > -->

When you understand a learning objective you will be able to explain it and put it into practice. 

<!-- > -->

**There will be learning objectives for each class.** You should test your knowledge by explaining the concepts to someone else and implement the learning objectives in code when the learning objectives are code. Some objectives are larger overarching concepts, in these cases, you should identify the learning objective in your code, your project as a whole, or in the larger software ecosystem or the world at large. 

<!-- > -->

**If you are having trouble understanding a learning objective you need to take action.** Discuss the topic with another student, talk with a TA, bring questions to class, talk to an instructor during lab or office hours. 

<!-- > -->

<!-- 

Success Skills Exercise - WOOP (5 to 10 mins)

https://drive.google.com/file/d/1vXiBzQ7AeHSMLJgvn3Ji-BMNvCayQIPH/view

-->

## HTML is Strucure <!--(5 min)-->

While HTML is just one piece of how websites are built, it is the _foundation_ upon which we build our websites. Without it, our websites would have no structure, or elements that we could style. Consider the following:

![html house](./images/html_house.gif)

<!-- v -->

We construct our websites by first laying down the foundation (our HTML elements) and then providing it with aesthetics and style (CSS). You can't style a house before you have the foundation and outline of it, so let's get started on learning how to build out our HTML elements!

<!-- > -->

### Why is this important?

- Without a knowledge of how to properly use HTML, we can't build out our websites! If you want to build a custom website, or even do any customization on website builders like Squarespace or Wix, you need to know HTML
- Knowing HTML is one thing, but using it properly is another. Knowing which elements to use for which scenario not only improves your website's structure, but also improves its SEO (Search Engine Optimization). By utilizing semantic HTML, you have a better chance of drawing users to your website by improving your appearance in search results!

<!-- > -->

## How do we use HTML? <!--(5 min)-->

HTML uses tags to "markup" a document. Tags describe and provide context to content. 

Below the `p`, or paragraph, tag describes the text Hello World as a paragraph. 

```html
<p>Hello World.</p>
```

The opening tag `<p>` is followed by a closing tag `</p>` which has a slash `/`.

<!-- > -->

### Combining Tags

Many different tags can be combined and nested one within another. 

```html
<article>
  <h1>HTML</html>
  <p><abbr>HTML</abbr> is the best!</p>
</article>
```

<!-- > -->

### Tags cannot overlap!

Good:

```HTML
<p><abbr>HTML</abbr> is the best!</p>
```

Bad: 
```HTML
<p><abbr>HTML</p></abbr> is the best!
```

(the `</p>` closes before the inner `</abbr>`)
<!-- .element: class="fragment" -->

<!-- > -->

## Combining Tags Activity <!--(15 min)-->

Translate the following tag combinations from english into HTML. When you're done, check your answers with a partner:

Imagine the following blocks of text, your job is to make them up using tags: 

Better get those flowers ASAP valentines day is around the corner!

Try this out on your own in code! Open this Repl and solve the problem there. 

<!-- https://repl.it/join/owsvoilk-mitchellhudson -->

Markup the following article:

```
Markup Language

From wikimedia
Hypertext Markup Language (HTML) is the standard markup language for creating web pages and web applications.

With Cascading Style Sheets (CSS) and JavaScript, it forms a triad of cornerstone technologies for the World Wide Web.[4]

Web browsers receive HTML documents from a web server or from local storage and render the documents into multimedia web pages. HTML describes the structure of a web page semantically and originally included cues for the appearance of the document.

Link: visit wiki
```

The text here is a snippet from wikipedia. It's an article about the HTML language. 
Look at what's there. Find the following: 

- Article
- Header
- Title	
- Subtitle 
- Two paragraphs
- Footer 
- Abbreviation 
- Link

Use these tags: 

- <article>
- <header>
- <h1>
- <p>
- <footer>
- <abbr>
- <a>

Think about these ideas:

The whole thing is an article. All of the content is related. 

The header and footer of an article always go inside the article. This shows they are related. 

```HTML
<article> 
  <header></header>
  other content
  <footer></footer>
</article>
```

The title might be an <h1> - <h6>
Subtitle could be a <p> or other tag like <small>.

<!-- 

<p>Better get those flowers <abbr>ASAP</abbr> <time>valentines day</time> is around the corner!</p>

1. Within a `div`, put an `h2` with the text "Hello World" and a `p` that says "Nice To Meet You"
1. Within a `p`, put an `abbr` with the text `HTML`, then within the rest of the `p`, put the text "is a hardware store"
1. Within an `article`, put a `p` with the text "do not forget the " followed by a `mark` that says "flowers ", and ending with "tonight" before closing out the `p`

 -->

<!--
Question 1:
<div>
    <h2>Hello World</h2>
    <p>Nice To Meet You</p>
</div>

Question 2:
<p><abbr>ACE</abbr> is a hardware store</p>

Question 3:
<article>
    <p>do not forget the <mark>flowers</mark> tonight </p>
</article>
 -->
 

<!-- > -->

## Semantic HTML <!--(15 min)-->

<!-- > -->

### What is semantic HTML?

**Semantic** (adj.): of or relating to meaning in language

To use a *word* semantically is to use a word in a way that properly aligns with its meaning.
<!-- .element: class="fragment" -->

**Semantic markup** is to use tags that properly align with the **content** the tags mark up.
<!-- .element: class="fragment" -->

<!-- > -->

### Some Examples

<!-- > -->

#### "Valentines day! ♥️"

How would you mark this up?
<!-- .element: class="fragment" -->

A time or date uses the `time` tag.
<!-- .element: class="fragment" -->

```html
<time>Valentines day! ♥️</time>
```
<!-- .element: class="fragment" -->

Or better
<!-- .element: class="fragment" -->
```html
<time datetime="2021-02-14">Valentines day! </time>
```
<!-- .element: class="fragment" -->

<!-- > -->

#### "HTML"

How would you mark this up? (seriously)
<!-- .element: class="fragment" -->

Abbreviations and acronyms use the `abbr` tag.
<!-- .element: class="fragment" -->

```html
<abbr>HTML</abbr>
```
<!-- .element: class="fragment" -->

Or, better
<!-- .element: class="fragment" -->

```html
<abbr title="Hyper Text Markup Language">HTML</abbr>
```
<!-- .element: class="fragment" -->

<!-- > -->

<abbr title="Hyper Text Markup Language">HTML</abbr> was invented by Tim Berners Lee.

**Important concept!**

Attributes are the values that appear within a tag. `title` and `datetime` in the last two examples. An attribute is always in the form of `name="value"`. The valus always appears in quotes. 

<!-- > -->

#### "How would you mark this up? (seriously)"

```HTML
<p>How would <em>you</em> mark this up? <strong>(seriously)</strong></p>
```
<!-- .element: class="fragment" -->

`em` and `strong` are inline tags that control the voice of what you are saying.
<!-- .element: class="fragment" -->

<em>Always</em> use inline tags <strong>inside a block!</strong>
<!-- .element: class="fragment" -->

<!-- > -->

### Sarcasm

What about a sarcasm tag?  
<!-- .element: class="fragment" -->

Would this be useful? Discuss... 
<!-- .element: class="fragment" -->

What tags would find useful for communication? Discuss... 
<!-- .element: class="fragment" -->

<!-- > -->

### Some Rules

<!-- > -->

- Pairs end with / - `<p>...</p>`
- Some tags don't have a pair - `<hr>`
- Tags can't overlap! - `<p><time>Valentines day!</time></p>`
- Attributes are name value pairs the value is always in quotes - `<img src="./picture.png">`

<!-- > -->

## Activity <!--(20 min)-->

Pair up and research tags. 

https://developer.mozilla.org/en-US/docs/Web/HTML/Element

Take a look at what the HTML5 Dr has to say about your tags: http://html5doctor.com

Choose **one tag from each category** to present to your classmates. Include an example of the tags in use to show context.

<!-- > -->

1.
- address
- article, section, aside
- nav, main
- footer, header
- h1-6, hgroup

2.
- blockquote
- dd, dl, dt, ul, ol, li
- figure, figcaption
- pre, code

3.
- a
- abbr, time, 
- dfn
- i, b, u, strong, em, sup, sub
- mark, del, ins, q

4.
- area
- audio, video, source, img, track

- embed, iframe, object

- canvas
- details, dialog, menu, menuitem, summary

<!-- > -->

## Check for understanding <!--7 min-->

Answer the following questions on your own (2 min), then pair with another student and discuss in a breakout room (2 min). We'll discuss as a group at the end (3 min):

1. Why should we use semantic HTML?
1. Why is the below considered bad practice?

```HTML
<p><abbr>HTML</p></abbr> is the best!
```

<!-- > -->

## BREAK <!--(10 min)-->

Take a ten minute break and wrap a tag around everything you see. 

<!-- > -->

## Lab

Let's get some practice with the first Homework! [Assignment 1](../assignments/01-Portfolio-Part-1-Structure.md) will be due at the beginning of next class. We'll submit it together during class.

Take some time right now to work on it, and submit one question you have about the homework to the slack channel!

<!-- > -->

### Homework 

[Assignment 1](../assignments/01-Portfolio-Part-1-Structure.md) will be due at the beginning of next class. We'll submit it together during class.

Post your questions about the homework in the class slack channel! Questions are encouraged!!

<!-- > -->

### Additional Resources

1. http://html5doctor.com
1. https://en.wikipedia.org/wiki/HTML
1. https://developer.mozilla.org/en-US/docs/Web/HTML/Element"""

if __name__ == "__main__":
    tutor = MarkdownTutor(lesson1_md, "Semantic HTML Tutor")

    print(f"👋 Welcome to {tutor.name}!")
    print("Ask me anything about the lesson. Type 'quit' to exit.\n")

    while True:
        user_input = input("🧑 You: ")
        if user_input.lower().strip() in ["quit", "exit", "bye"]:
            print("👋 Goodbye! Keep practicing your HTML!")
            break

        answer = tutor.ask(user_input)
        print(f"🎓 {tutor.name}: {answer}\n")
