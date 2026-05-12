import json
import os
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

llm = ChatAnthropic(
    model="claude-haiku-4-5-20251001",
    anthropic_api_key=ANTHROPIC_API_KEY,
    max_tokens=512
)


def demo_basic_chain():
    print("\n--- DEMO 1: Basic Prompt Chain ---")

    prompt = ChatPromptTemplate.from_template(
        "You are a cybersecurity analyst. In 2 sentences, explain what {topic} is "
        "and why it matters to defense contractors."
    )

    chain = prompt | llm | StrOutputParser()

    result = chain.invoke({"topic": "CVE scoring (CVSS)"})
    print(result)


def demo_text_chunking():
    print("\n--- DEMO 2: Text Chunking ---")

    long_article = """
    A critical zero-day vulnerability has been discovered in OpenSSL affecting versions 
    3.0.0 through 3.0.6. The vulnerability allows remote attackers to execute arbitrary 
    code by sending a specially crafted certificate chain. This affects millions of servers 
    worldwide including those running Apache, Nginx, and various VPN solutions commonly 
    used in enterprise environments. CISA has issued an emergency directive requiring all 
    federal agencies to patch within 48 hours. Defense contractors using OpenSSL in 
    embedded systems or firmware are particularly at risk. The vulnerability has been 
    assigned CVE-2022-3602 and CVE-2022-3786 with CVSS scores of 9.8 and 7.5 respectively.
    Patches are available in OpenSSL 3.0.7 and organizations should prioritize updating 
    internet-facing systems first. Binary analysis of affected libraries using tools like 
    BinLens can help identify vulnerable components in compiled software.
    """ * 3

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " "]
    )

    chunks = splitter.split_text(long_article)
    print(f"Original length: {len(long_article)} chars")
    print(f"Split into {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i+1} ({len(chunk)} chars): {chunk[:80]}...")


def demo_article_summarization():
    print("\n--- DEMO 3: Summarizing Real Articles ---")

    articles_path = os.path.join(
        os.path.dirname(__file__), "..", "week2", "all_articles.json"
    )

    try:
        with open(articles_path, "r", encoding="utf-8") as f:
            articles = json.load(f)
    except FileNotFoundError:
        print("all_articles.json not found — make sure week2/async_crawling.py ran first.")
        return

    summarize_prompt = ChatPromptTemplate.from_template(
        """You are a threat intelligence analyst for a defense contractor.

Summarize this cybersecurity article in exactly 3 bullet points:
- Key threat or vulnerability
- Who is affected
- Recommended action

Article title: {title}
Article summary: {summary}

Respond with only the 3 bullet points."""
    )

    summarize_chain = summarize_prompt | llm | StrOutputParser()

    for article in articles[:3]:
        print(f"\nArticle: {article.get('title', 'No title')[:60]}...")
        result = summarize_chain.invoke({
            "title": article.get("title", ""),
            "summary": article.get("summary", article.get("url", "No content"))
        })
        print(result)
        print("-" * 50)


def demo_sequential_chain():
    print("\n--- DEMO 4: Sequential Chain (Two-Stage Analysis) ---")

    extract_prompt = ChatPromptTemplate.from_template(
        "Extract the CVE ID, affected software, and CVSS score from this text. "
        "If not present, write 'Not specified'. Text: {raw_text}"
    )

    action_prompt = ChatPromptTemplate.from_template(
        "Given these vulnerability facts: {extracted_facts}\n\n"
        "Write a one-sentence patch priority recommendation for a defense contractor's IT team."
    )

    parser = StrOutputParser()

    sequential_chain = (
        extract_prompt
        | llm
        | parser
        | (lambda extracted: action_prompt.invoke({"extracted_facts": extracted}))
        | llm
        | parser
    )

    raw_text = (
        "A buffer overflow in libssl version 1.1.1 (CVE-2023-0286, CVSS 7.4) "
        "allows attackers to crash TLS servers via malformed ASN.1 certificates."
    )

    result = sequential_chain.invoke({"raw_text": raw_text})
    print(f"Input: {raw_text}")
    print(f"\nFinal recommendation: {result}")


def run_demos():
    demo_basic_chain()
    demo_text_chunking()
    demo_article_summarization()
    demo_sequential_chain()
    print("\n✅ LangChain basics complete!")


if __name__ == "__main__":
    run_demos()