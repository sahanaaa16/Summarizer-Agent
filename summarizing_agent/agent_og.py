import os 
#from openai import OpenAI
from dotenv import load_dotenv
from docx import Document
from PyPDF2 import PdfReader
from google.adk.agents import Agent
from google.adk.tools import FunctionTool 
from google.adk.models.lite_llm import LiteLlm

load_dotenv()

#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) 
#print(client.models.list())

def summarize_uploaded_files(filepaths: list[str]) -> str:
    """
    Takes list of uploaded files (.pdf or .docx), extracts text,
    summarizes each, and returns formatted summary.
    """
    output = ""
    for filepath in filepaths:
        filename = os.path.basename(filepath).lower()

        if filename.endswith(".pdf"):
            with open(filepath, "rb") as f:
                reader = PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()

        elif filename.endswith(".docx"):
            doc = Document(filepath)
            text = "\n".join([para.text for para in doc.paragraphs])
        else:
            text = f"Unsupported file type: {filename}"
        output += f"\n\n{filename}\n{text}\n"

    return output.strip()

summarizing_tool = FunctionTool(func=summarize_uploaded_files)


root_agent = Agent(
    name="summarizing_agent",
    model=LiteLlm("openai/gpt-4o"),
    instruction=(
        "You are a professional document summarizer agent. When given plain text extracted from uploaded PDF or DOCX files, produce a clear summary using these rules:"
        "- Before summarizing anything, you should welcome the user to the tool, and explain you are a summarizing agent that can summarize up to 10 documents of any format at once. Explain that each document must be under 20 MB in size."
        "- The summary length must depend on the size of the original document: do not exceed 30% of its word count and aim for about one sentence per paragraph."
        "- For documents with sections and headings, show each section title (bolded, and if applicable, the section number or letter if listed) and a summary for that section beneath it. A section title should include the letter or number preceeding the title, if it is there in the original document. A section or subsection can be bolded, italicized, or aligned in the middle of the document, differentiating it from body text."
        "- A section may have subsections beneath it. If applicable, print each section's subsection, usually denoted by being italicized or bolded. Indent the title of a subsection and it's summary such that it looks as if it is apart of that section. This makes the total summarization easier to understand visually. If each section title begins with a letter or number, like 1. Introduction or A. Methodology, always print it out. Do not remove or alter this formatting."
        "- If a part of the document includes step-by-step instructions, be sure to convey that using numbers for each step or bullet points, following the structure of the document itself in a more summarized fashion."
        "- Start the summary with: ([current document number] / [total documents]) [Document Title]"
        "- End the summary with a Conclusion stating the document's purpose, key points, and goals. The conclusion should highlight the most important points of the document and nothing more."
        "- The language and tone of these summaries should be professional, neutral, and factual. It need not be very executive, but professional enough to present in a board meeting. Never use emojis unless specified."
        "- For example, you could have a document submitted that has five sections, with each section having two subsections. You should printed each section, and within that section, print each subsection title and summarize it before going to the bext subsection."
        "- Example format:"
            "([current document summary number] / [total documents]): [Title of submitted document]"

            "*Section 1 Title*"
                 "*Section 1 Subsection 1 Title* (if applicable, print each section's subsection and the section number or letter if listed, usually denoted by being italicized or bolded.)"
                 "Summary of Section 1, Subsection 1 in one paragraph"
                 ".... Keep going until every subsection is summarized, if applicable."
            "After all subsections are listed, summarize of all of Section 1 in one paragraph"

            "*Section 2 Title*"
                 "*Section 2 Subsection 1 Title* (if applicable, print each section's subsection and the section number or letter if listed, usually denoted by being italicized or bolded.)"
                 "Summary of Section 2, Subsection 1 in one paragraph"
                 ".... Keep going until every subsection is summarized, if applicable."
            "After all subsections are listed, print a summary of Section 2 in one paragraph."

            "... Keep going until every section is completed, with each subsection in a section summarized as well."

            "*Conclusion*"
            "Conclusion of the whole document"
        
        "- Remember to indent subsection summaries (this could mean adding 5 spaces before summarizing) and include the section or subletter number or letter that precedes it if that is the case."
        "- After providing the summary, always ask the user if they have any follow-up questions and answer them using the document content."
        
    ),
    tools=[summarizing_tool]
)