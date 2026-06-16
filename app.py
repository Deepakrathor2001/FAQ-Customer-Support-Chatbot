import os
import csv
import json
import math
import re
import streamlit as st
from anthropic import Anthropic

DATASET_LOAD_STATUS = []


# ------------------------------------------------------------------ #
#  STEP 1 - Load all datasets and build the knowledge base            #
# ------------------------------------------------------------------ #

PROJECT_ROOT = os.path.dirname(__file__)
EXTERNAL_DATASET_ROOT = r"D:\PROJECTS AND PROGRAMMING\DATASET"
TEXT_ENCODINGS = ("utf-8-sig", "cp1252", "latin-1")


def clean_text(value):
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def make_record(source, question, answer):
    question = clean_text(question)
    answer = clean_text(answer)
    if question and answer:
        return {"source": source, "question": question, "answer": answer}
    return None


def record_dataset_status(source_name, path, count, error=None):
    DATASET_LOAD_STATUS.append({
        "source": source_name,
        "path": path,
        "count": count,
        "error": error
    })


def load_ecommerce_data(path):
    records = []
    if not os.path.exists(path):
        record_dataset_status("E-Commerce", path, 0, "File not found")
        return records
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = data.get("questions", data) if isinstance(data, dict) else data
        for item in items:
            record = make_record("E-Commerce", item.get("question", ""), item.get("answer", ""))
            if record:
                records.append(record)
    except Exception as e:
        record_dataset_status("E-Commerce", path, 0, str(e))
        st.warning("Could not load ecommerce dataset: " + str(e))
    else:
        record_dataset_status("E-Commerce", path, len(records))
    return records


def load_json_faq(path, source_name, q_key="question", a_key="answer"):
    records = []
    if not os.path.exists(path):
        record_dataset_status(source_name, path, 0, "File not found")
        return records
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = data if isinstance(data, list) else data.get("questions", [])
        for item in items:
            record = make_record(source_name, item.get(q_key, ""), item.get(a_key, ""))
            if record:
                records.append(record)
    except Exception as e:
        record_dataset_status(source_name, path, 0, str(e))
        st.warning("Could not load " + source_name + " dataset: " + str(e))
    else:
        record_dataset_status(source_name, path, len(records))
    return records


def load_custom_dataset(base):
    entries = []
    filepath = os.path.join(base, "custom_faq_dataset.json")
    if not os.path.exists(filepath):
        record_dataset_status("Custom", filepath, 0, "File not found")
        return entries
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            record = make_record(
                item.get("category", "Custom"),
                item.get("question", ""),
                item.get("answer", "")
            )
            if record:
                entries.append(record)
    except Exception as e:
        record_dataset_status("Custom", filepath, 0, str(e))
        st.warning("Could not load custom dataset: " + str(e))
    else:
        record_dataset_status("Custom", filepath, len(entries))
    return entries


def load_csv_dataset(path, source_name, question_fields, answer_fields, metadata_fields=None):
    records = []
    metadata_fields = metadata_fields or []
    if not os.path.exists(path):
        record_dataset_status(source_name, path, 0, "File not found")
        return records
    try:
        csv.field_size_limit(1024 * 1024 * 50)
        last_error = None
        for encoding in TEXT_ENCODINGS:
            records = []
            try:
                with open(path, "r", encoding=encoding, newline="") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        question_parts = [row.get(field, "") for field in question_fields]
                        answer_parts = [row.get(field, "") for field in answer_fields]
                        metadata_parts = []
                        for field in metadata_fields:
                            value = clean_text(row.get(field, ""))
                            if value:
                                metadata_parts.append(field.replace("_", " ").title() + ": " + value)

                        question = "\n".join(part for part in question_parts if clean_text(part))
                        answer = "\n".join(part for part in answer_parts if clean_text(part))
                        if metadata_parts:
                            answer = (answer + "\n" if answer else "") + "\n".join(metadata_parts)

                        record = make_record(source_name, question, answer)
                        if record:
                            records.append(record)
                break
            except UnicodeDecodeError as e:
                last_error = e
        else:
            raise last_error
    except Exception as e:
        record_dataset_status(source_name, path, 0, str(e))
        st.warning("Could not load " + source_name + " dataset: " + str(e))
    else:
        record_dataset_status(source_name, path, len(records))
    return records


def load_tab_separated_qa(path, source_name):
    records = []
    if not os.path.exists(path):
        record_dataset_status(source_name, path, 0, "File not found")
        return records
    try:
        last_error = None
        for encoding in TEXT_ENCODINGS:
            records = []
            try:
                with open(path, "r", encoding=encoding, newline="") as f:
                    reader = csv.DictReader(f, delimiter="\t")
                    for row in reader:
                        source = source_name
                        title = clean_text(row.get("ArticleTitle", ""))
                        if title:
                            source += " - " + title.replace("_", " ")
                        record = make_record(source, row.get("Question", ""), row.get("Answer", ""))
                        if record:
                            records.append(record)
                break
            except UnicodeDecodeError as e:
                last_error = e
        else:
            raise last_error
    except Exception as e:
        record_dataset_status(source_name, path, 0, str(e))
        st.warning("Could not load " + source_name + " dataset: " + str(e))
    else:
        record_dataset_status(source_name, path, len(records))
    return records


def load_text_data_toc(path, source_name):
    records = []
    if not os.path.exists(path):
        record_dataset_status(source_name, path, 0, "File not found")
        return records
    try:
        text_data_dir = os.path.join(os.path.dirname(path), "text_data")
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                filename = clean_text(row.get("file", ""))
                if not filename:
                    continue
                article_path = os.path.join(text_data_dir, filename)
                if not os.path.exists(article_path):
                    continue
                with open(article_path, "r", encoding="utf-8", errors="ignore") as article_file:
                    article_text = article_file.read()
                question = "Reference article: " + filename
                record = make_record(source_name, question, article_text)
                if record:
                    records.append(record)
    except Exception as e:
        record_dataset_status(source_name, path, 0, str(e))
        st.warning("Could not load " + source_name + " dataset: " + str(e))
    else:
        record_dataset_status(source_name, path, len(records))
    return records


def build_knowledge_base():
    DATASET_LOAD_STATUS.clear()
    ecommerce_path = os.path.join(PROJECT_ROOT, "E-Commerce FAQS dataset")
    legacy_data_path = os.path.join(PROJECT_ROOT, "data")

    all_records = []

    all_records += load_ecommerce_data(os.path.join(ecommerce_path, "Ecommerce_FAQ_Chatbot_dataset.json"))
    all_records += load_json_faq(os.path.join(legacy_data_path, "Amazon_sagemaker_Faq.txt"), "Amazon SageMaker")
    all_records += load_json_faq(os.path.join(legacy_data_path, "faq_results.txt"), "Air India Express", q_key="Question", a_key="Answer")
    all_records += load_json_faq(os.path.join(legacy_data_path, "HDFC_Faq.txt"), "HDFC Bank")
    all_records += load_json_faq(os.path.join(legacy_data_path, "Aadhar_Faq.txt"), "Aadhaar")
    all_records += load_json_faq(os.path.join(legacy_data_path, "Sevenhillshospital_faq.txt"), "SevenHills Hospital")
    all_records += load_json_faq(os.path.join(legacy_data_path, "Tata_comm_faq.txt"), "Tata Communications")
    all_records += load_custom_dataset(legacy_data_path)

    all_records += load_csv_dataset(
        os.path.join(EXTERNAL_DATASET_ROOT, "Medical dataset", "medquad.csv"),
        "Medical - MedQuAD",
        ["question"],
        ["answer"],
        ["source", "focus_area"]
    )
    all_records += load_csv_dataset(
        os.path.join(EXTERNAL_DATASET_ROOT, "IT customer support dataset", "full_dataset.csv"),
        "IT Customer Support",
        ["input"],
        ["target"]
    )
    all_records += load_csv_dataset(
        os.path.join(EXTERNAL_DATASET_ROOT, "Financail  dataset", "Financial-QA-10k.csv"),
        "Financial QA",
        ["question"],
        ["answer"],
        ["context", "ticker", "filing"]
    )
    all_records += load_csv_dataset(
        os.path.join(EXTERNAL_DATASET_ROOT, "Banking dataset", "Dataset_Banking_chatbot.csv"),
        "Banking",
        ["Query"],
        ["Response"]
    )

    education_path = os.path.join(EXTERNAL_DATASET_ROOT, "Education dataset")
    ticket_metadata = ["type", "queue", "priority", "language", "business_type"]
    all_records += load_csv_dataset(
        os.path.join(education_path, "aa_dataset-tickets-multi-lang-5-2-50-version.csv"),
        "Education Tickets - Multi Lang 5-2-50",
        ["subject", "body"],
        ["answer"],
        ticket_metadata
    )
    all_records += load_csv_dataset(
        os.path.join(education_path, "dataset-tickets-german_normalized.csv"),
        "Education Tickets - German Normalized",
        ["subject"],
        ["body"],
        ["queue", "priority", "language"]
    )
    all_records += load_csv_dataset(
        os.path.join(education_path, "dataset-tickets-german_normalized_50_5_2.csv"),
        "Education Tickets - German Normalized 50-5-2",
        ["subject"],
        ["body"],
        ["queue", "priority", "language"]
    )
    all_records += load_csv_dataset(
        os.path.join(education_path, "dataset-tickets-multi-lang3-4k.csv"),
        "Education Tickets - Multi Lang 3-4k",
        ["subject", "body"],
        ["answer"],
        ticket_metadata
    )
    all_records += load_csv_dataset(
        os.path.join(education_path, "dataset-tickets-multi-lang-4-20k.csv"),
        "Education Tickets - Multi Lang 4-20k",
        ["subject", "body"],
        ["answer"],
        ticket_metadata
    )

    archive_path = os.path.join(EXTERNAL_DATASET_ROOT, "archive (4)")
    all_records += load_tab_separated_qa(os.path.join(archive_path, "S08_question_answer_pairs.txt"), "Wikipedia QA S08")
    all_records += load_tab_separated_qa(os.path.join(archive_path, "S09_question_answer_pairs.txt"), "Wikipedia QA S09")
    all_records += load_tab_separated_qa(os.path.join(archive_path, "S10_question_answer_pairs.txt"), "Wikipedia QA S10")
    all_records += load_text_data_toc(os.path.join(archive_path, "text_data_toc.csv"), "Wikipedia Article Text")

    return all_records


# ------------------------------------------------------------------ #
#  STEP 2 - TF-IDF based retrieval (no external vector libraries)     #
# ------------------------------------------------------------------ #

def tokenize(text):
    text = text.lower()
    tokens = re.findall(r"\w+", text, flags=re.UNICODE)
    stopwords = {
        "i", "me", "my", "we", "our", "you", "your", "he", "she", "it",
        "they", "is", "are", "was", "were", "be", "been", "being", "have",
        "has", "had", "do", "does", "did", "will", "would", "should", "could",
        "may", "might", "shall", "can", "a", "an", "the", "and", "or", "but",
        "in", "on", "at", "to", "for", "of", "with", "by", "from", "about",
        "what", "how", "when", "where", "who", "which", "why", "that", "this",
        "if", "so", "as", "not", "no", "please", "yes", "want", "need", "get"
    }
    return [t for t in tokens if t not in stopwords and len(t) > 1]


def build_tfidf_index(records):
    num_docs = len(records)
    doc_tokens_list = []
    df = {}

    for record in records:
        combined = record["question"] + " " + record["answer"]
        tokens = tokenize(combined)
        token_set = set(tokens)
        doc_tokens_list.append(tokens)
        for token in token_set:
            df[token] = df.get(token, 0) + 1

    idf = {}
    for term, freq in df.items():
        idf[term] = math.log((num_docs + 1) / (freq + 1)) + 1.0

    doc_vectors = []
    for tokens in doc_tokens_list:
        tf_counts = {}
        for t in tokens:
            tf_counts[t] = tf_counts.get(t, 0) + 1
        total = len(tokens) if tokens else 1
        vec = {}
        for t, count in tf_counts.items():
            tf = count / total
            vec[t] = tf * idf.get(t, 1.0)
        doc_vectors.append(vec)

    return doc_vectors, idf


def cosine_similarity(vec_a, vec_b):
    if not vec_a or not vec_b:
        return 0.0
    dot = sum(vec_a.get(t, 0.0) * vec_b.get(t, 0.0) for t in vec_b)
    mag_a = math.sqrt(sum(v * v for v in vec_a.values()))
    mag_b = math.sqrt(sum(v * v for v in vec_b.values()))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def retrieve_top_chunks(query, doc_vectors, idf, records, top_k=5):
    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    tf_counts = {}
    for t in query_tokens:
        tf_counts[t] = tf_counts.get(t, 0) + 1
    total = len(query_tokens)

    query_vec = {}
    for t, count in tf_counts.items():
        tf = count / total
        query_vec[t] = tf * idf.get(t, 1.0)

    scored = []
    for i, doc_vec in enumerate(doc_vectors):
        score = cosine_similarity(query_vec, doc_vec)
        if score > 0:
            scored.append((score, i))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_results = []
    for score, idx in scored[:top_k]:
        top_results.append({
            "score": score,
            "source": records[idx]["source"],
            "question": records[idx]["question"],
            "answer": records[idx]["answer"]
        })

    return top_results


#  STEP 3 - Build the prompt with retrieved context (RAG)        

def build_rag_system_prompt(retrieved_chunks):
    context_block = ""
    for i, chunk in enumerate(retrieved_chunks, start=1):
        answer = chunk["answer"]
        if len(answer) > 1800:
            answer = answer[:1800] + "..."
        context_block += (
            "Source: " + chunk["source"] + "\n"
            "Question: " + chunk["question"] + "\n"
            "Answer: " + answer + "\n\n"
        )

    system_prompt = (
        "You are a helpful and professional AI customer support assistant. "
        "You have been trained on FAQ data from multiple organizations including "
        "E-Commerce, medical, IT support, financial, banking, education ticket, "
        "and Wikipedia-style question-answer datasets.\n\n"
        "You will be given relevant FAQ context retrieved from this knowledge base. "
        "Use this context to answer the user question as accurately as possible.\n\n"
        "Rules you must follow:\n"
        "- Answer only based on the retrieved context provided below.\n"
        "- If the context does not contain enough information to answer the question, "
        "say that you do not have that specific information and suggest the user contact "
        "the relevant organization directly.\n"
        "- Be polite, clear, and professional at all times.\n"
        "- Do not make up information that is not in the context.\n"
        "- Keep answers concise and easy to understand.\n"
        "- Respond in English only.\n"
        "- Do not use emojis or special symbols.\n"
        "- When the question matches a specific organization in the context, "
        "mention which organization the information comes from.\n\n"
        "Retrieved FAQ Context:\n"
        "---------------------\n"
        + context_block +
        "---------------------\n"
        "Now answer the user question using only the above context."
    )

    return system_prompt


# ------------------------------------------------------------------ #
#  STEP 4 - Get answer from Claude using RAG context                  #
# ------------------------------------------------------------------ #

def get_rag_answer(user_question, doc_vectors, idf, records):
    client = Anthropic()
    retrieved = retrieve_top_chunks(user_question, doc_vectors, idf, records, top_k=5)

    if not retrieved:
        system_prompt = (
            "You are a helpful customer support assistant. "
            "The user asked a question but no relevant FAQ context was found. "
            "Politely tell the user that you do not have information about that topic "
            "and suggest they contact the relevant support team directly."
        )
    else:
        system_prompt = build_rag_system_prompt(retrieved)

    st.session_state.chat_history.append({
        "role": "user",
        "content": user_question
    })

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        system=system_prompt,
        messages=st.session_state.chat_history
    )

    answer = response.content[0].text

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": answer
    })

    return answer, retrieved


# ------------------------------------------------------------------ #
#  STEP 5 - Streamlit UI                                              #
# ------------------------------------------------------------------ #

def initialize_session():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "kb_loaded" not in st.session_state:
        st.session_state.kb_loaded = False
    if "records" not in st.session_state:
        st.session_state.records = []
    if "doc_vectors" not in st.session_state:
        st.session_state.doc_vectors = []
    if "idf" not in st.session_state:
        st.session_state.idf = {}
    if "dataset_load_status" not in st.session_state:
        st.session_state.dataset_load_status = []


def load_kb_once():
    if not st.session_state.kb_loaded:
        with st.spinner("Loading knowledge base from all datasets. Please wait..."):
            records = build_knowledge_base()
            doc_vectors, idf = build_tfidf_index(records)
            st.session_state.records = records
            st.session_state.doc_vectors = doc_vectors
            st.session_state.idf = idf
            st.session_state.dataset_load_status = list(DATASET_LOAD_STATUS)
            st.session_state.kb_loaded = True
        sources = set(record["source"] for record in records)
        st.success(
            "Knowledge base loaded. "
            + str(len(records))
            + " entries indexed across "
            + str(len(sources))
            + " sources."
        )


def render_sidebar(records):
    with st.sidebar:
        st.header("Knowledge Base")
        st.write("This chatbot is trained on FAQ data from the following sources:")

        sources = {}
        for r in records:
            sources[r["source"]] = sources.get(r["source"], 0) + 1

        for source, count in sorted(sources.items()):
            st.write("- " + source + " (" + str(count) + " FAQs)")

        st.divider()
        st.write("Total FAQ entries indexed: " + str(len(records)))
        with st.expander("Dataset load status"):
            for item in st.session_state.dataset_load_status:
                label = item["source"] + ": " + str(item["count"]) + " records"
                if item["error"]:
                    st.warning(label + " (" + item["error"] + ")")
                else:
                    st.success(label)
        st.divider()
        st.subheader("How RAG works here")
        st.write(
            "When you ask a question, the system uses TF-IDF similarity to find "
            "the most relevant FAQ entries from all datasets. Those entries are "
            "passed to Claude as context, and Claude generates a precise answer "
            "based only on that retrieved information."
        )
        st.divider()

        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.session_state.chat_history = []
            st.rerun()


def render_chat():
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.write(msg["content"])
        elif msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.write(msg["content"])
            if "sources" in msg and msg["sources"]:
                with st.expander("Retrieved Sources (" + str(len(msg["sources"])) + " matched)"):
                    for chunk in msg["sources"]:
                        st.write(
                            "Source: " + chunk["source"] +
                            " | Score: " + str(round(chunk["score"], 3))
                        )
                        st.write("Matched Q: " + chunk["question"])
                        st.divider()


def main():
    st.set_page_config(
        page_title="AI Customer Support FAQ Chatbot",
        layout="wide"
    )

    st.title("AI Customer Support FAQ Chatbot")
    st.caption(
        "Answer Genareted by Retrieval Augmented Generation. "
    )

    initialize_session()
    load_kb_once()

    records = st.session_state.records
    doc_vectors = st.session_state.doc_vectors
    idf = st.session_state.idf

    render_sidebar(records)

    if len(st.session_state.messages) == 0:
        with st.chat_message("assistant"):
            st.write(
                "Hello, welcome to the AI Customer Support Assistant. "
                "I have been trained on FAQ data from multiple organizations. "
                "You can ask me about online shopping, banking, medical topics, "
                "finance, IT support, education tickets, or reference QA. "
                "How can I help you today?"
            )

    render_chat()

    user_input = st.chat_input("Ask your question here...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Searching knowledge base and generating answer..."):
                try:
                    answer, retrieved = get_rag_answer(
                        user_input, doc_vectors, idf, records
                    )
                    st.write(answer)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": retrieved
                    })
                    if retrieved:
                        with st.expander("Retrieved Sources (" + str(len(retrieved)) + " matched)"):
                            for chunk in retrieved:
                                st.write(
                                    "Source: " + chunk["source"] +
                                    " | Score: " + str(round(chunk["score"], 3))
                                )
                                st.write("Matched Q: " + chunk["question"])
                                st.divider()
                except Exception as e:
                    error_msg = (
                        "I am sorry, something went wrong while processing your request. "
                        "Please try again or contact support directly."
                    )
                    st.write(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "sources": []
                    })


if __name__ == "__main__":
    main()
