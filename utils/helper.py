def process_keywords(s: str):
    keywords = s.split(',')
    keywords = ["\"" + keyword.strip() + "\"" for keyword in keywords]
    return ' '.join(keywords)