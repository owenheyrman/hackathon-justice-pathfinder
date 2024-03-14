from haystack.document_stores import InMemoryDocumentStore
from haystack import Document
import os
from haystack.nodes import BM25Retriever
from utils import load_config
from haystack.nodes import PromptNode, PromptTemplate, AnswerParser
from prompt_templates import rag_prompt
from haystack.pipelines import Pipeline


class HaystackPipeline:
        def __init__(self):
                self.document_store = InMemoryDocumentStore(use_bm25=True)
                self.fill_document_store()

                self.n_documents_to_retrieve = 3
                self.retriever = retriever = BM25Retriever(document_store=self.document_store, top_k=self.n_documents_to_retrieve)
                
                self.config = load_config()
                self.openai_api_key = self.config["openAI_key"]
                
                self.prompt_template = PromptTemplate(prompt=rag_prompt, output_parser=AnswerParser())
                self.prompt_node = PromptNode(model_name_or_path="gpt-4-turbo-preview", api_key=self.openai_api_key, default_prompt_template=self.prompt_template,  max_length=1000)

                self.pipeline = Pipeline()
                self.pipeline.add_node(component=self.retriever, name="retriever", inputs=["Query"])
                self.pipeline.add_node(component=self.prompt_node, name="prompt_node", inputs=["retriever"])

        
        def run(self, query):
                result = self.pipeline.run(query=query)
                #return result <- for when we need to know which documents etc
                return(result["answers"][0].answer)




        def fill_document_store(self):
                directory = "./data/website/"

                documents = []

                for file in os.listdir(directory):
                    if file.endswith('.txt'):
                        with open(os.path.join(directory, file), encoding='utf-8') as f:
                            file_contents = f.read()
                            file_name = str(file)

                            documents.append(Document(content=file_contents, meta={"title": file_name,}))

                self.document_store.write_documents(documents)


              
                