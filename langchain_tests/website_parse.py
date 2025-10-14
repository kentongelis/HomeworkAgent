from langchain_unstructured import UnstructuredLoader

loader = UnstructuredLoader(
    web_url="https://github.com/Tech-at-DU/ACS-4310-Data-Visualization-and-Web-Graphics"
)
docs = loader.load()

for doc in docs:
    print(doc.page_content)
