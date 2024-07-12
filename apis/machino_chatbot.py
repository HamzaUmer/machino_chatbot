from flask_restx import Namespace, Resource, reqparse
from flask import Flask, request, jsonify, make_response
import os
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredFileLoader
from pymongo import MongoClient
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

api = Namespace('qna', description='Machinoweb docs stored and retrieved using mongoDB')
os.environ["OPENAI_API_KEY"] = os.environ.get("open_ai_api_key")
MONGODB_ATLAS_CLUSTER_URI = os.environ.get("mongo_uri")
client = MongoClient(MONGODB_ATLAS_CLUSTER_URI)

DB_NAME = "machino"
COLLECTION_NAME = "chatbot"
ATLAS_VECTOR_SEARCH_INDEX_NAME = "machino_index"

MONGODB_COLLECTION = client[DB_NAME][COLLECTION_NAME]

# Load the PDF
def process_and_store_documents():
    loader = UnstructuredFileLoader("apis/docs/services_detail.docx")
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    docs = text_splitter.split_documents(data)
    # Set manual URL for each document
    manual_url = "https://docs.google.com/document/d/1Jdn3O6oI3ezXVVAXRuo1gEsLHfthyqH3/edit?usp=drive_link&ouid=116763014659288659605&rtpof=true&sd=true"
    for doc in docs:
        doc.metadata['source'] = manual_url  # Set manual URL for source
    print("Docs after splitting",docs[0])

    # insert the documents in MongoDB Atlas with their embedding
    vector_search = MongoDBAtlasVectorSearch.from_documents(
        documents=docs,
        embedding=OpenAIEmbeddings(disallowed_special=()),
        collection=MONGODB_COLLECTION,
        index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
    )
# process_and_store_documents()
vector_search = MongoDBAtlasVectorSearch.from_connection_string(
    MONGODB_ATLAS_CLUSTER_URI,
    DB_NAME + "." + COLLECTION_NAME,
    OpenAIEmbeddings(disallowed_special=()),
    index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
)

qa_retriever = vector_search.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5},
)

prompt_template = """Use the following pieces of context to answer the question at the end by summarizing the context. 
If the answer includes a list of technical skills, or any other numerically listed items, present the answer in a numeric list, each item on a new line. 
If you don't know the answer, just say you don't know, don't try to make up an answer.
{context}

Question: {question}
Answer: """
PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context","question"]
)

qa = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    chain_type="stuff",
    retriever=qa_retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT},
)

# Define the parser and request args
parser = reqparse.RequestParser()
parser.add_argument('query', type=str, required=True, help='Query string for the chatbot', location='json')

@api.route('/chatbot')
class MachinoQnA(Resource):
    @api.expect(parser)
    def post(self):
        args = parser.parse_args()
        query = args['query']
        results = qa({"query": query})
        print("Result", results['source_documents'][0].metadata['source'])
        # Check if there are any results
        if results:    
            # Return the extracted page_content in the response
            return make_response(jsonify({"answer": results['result'], "query": query, "url":results['source_documents'][0].metadata['source']}), 200)
        else:
            # If no results found, return an empty response
            return make_response(jsonify({"answer": "No similar documents found", "query": query,"url": "No URL find"}), 404)