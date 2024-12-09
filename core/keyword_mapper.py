import re
import os
import sys
import spacy # type: ignore

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))

from log.logger import setup_logger




logger = setup_logger("keyword_mapper_logs")

nlp = spacy.load("en_core_web_sm")

# nlp = spacy.load("en_core_web_lg")


def match_keywords(text, keywords):
    matches = []
    for keyword in keywords:
        # Add word boundary `\b` to the keyword to avoid partial matches
        pattern = fr'\b{re.escape(keyword)}\b'
        found = re.findall(pattern, text, re.IGNORECASE)  # case insensitive match
        matches.extend(found)
    return matches

def match_keywords_with_punctuation(text, keywords):
    matches = []
    for keyword in keywords:
        # Regex to match keywords surrounded by word boundaries or punctuation marks
        pattern = fr'(?<!\w){re.escape(keyword)}(?!\w)'  # Ensures it's not preceded or followed by a word character
        found = re.findall(pattern, text, re.IGNORECASE)  # Case-insensitive
        matches.extend(found)
    return matches



def classify_tender(keywords, category_keywords):
    # Initialize category scores
    category_scores = {category: 0 for category in category_keywords}

    # Count keyword occurrences for each category
    for keyword in keywords:
        for category, category_kw_list in category_keywords.items():
            # Use lowercasing and handle variations in keyword case
            if keyword.lower() in [kw.lower() for kw in category_kw_list]:
                category_scores[category] += 1

    # Sort categories by their scores in descending order
    sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)

    # Get the highest score from the sorted list
    highest_score = sorted_categories[0][1]

    # Handle the case where no keywords match any category
    if highest_score == 0:
        return "ambiguous"

    # Get all categories with the highest score
    top_categories = [category for category, score in sorted_categories if score == highest_score]

    # If there's more than one category with the highest score, return "ambiguous"
    if len(top_categories) > 1:
        return "ambiguous"

    # Return the category with the highest score
    return top_categories[0]
    
        
    

# def map_keywords_to_categories(tender_documents, predefined_keywords):
    
#     logger.info("Mapping keywords to categories.")
    
#     relevant = False
#     matched_categories = set()
#     keyword_occurrences = []
#     extracted_keywords = []

#     # Create a flat list of (category, keyword) tuples for easy lookup
#     keyword_category_map = {}
#     for category, keywords in predefined_keywords.items():
#         for kw in keywords:
#             keyword_category_map[kw.lower()] = category

#     # for page in tender_documents:
#     #     doc = nlp(page['text'])
#     #     for token in doc:
#     #         lemma = token.lemma_.lower()
#     #         if lemma in keyword_category_map:
#     #             relevant = True
#     #             category = keyword_category_map[lemma]
#     #             matched_categories.add(category)
#     #             occurrence = f"Keyword '{token.text}' found on page {page['page']}"
#     #             keyword_occurrences.append(occurrence)
    
#     # for page in tender_documents:
#     #     doc = nlp(page['text'])
#     #     doc_text = page['text']
#     #     for token in doc:
#     #         lemma = token.lemma_.lower()
#     #         if lemma in keyword_category_map:
#     #             relevant = True
#     #             category = keyword_category_map[lemma]
#     #             matched_categories.add(category)
#     #             extracted_keywords.append(lemma) 

#     #             # Extracting context around the keyword (5 words before and after)
#     #             keyword_position = token.idx
#     #             start_pos = max(0, keyword_position - 35)  # Adjust to extract context
#     #             end_pos = min(len(doc_text), keyword_position + 35)
#     #             context = doc_text[start_pos:end_pos].strip()

#     #             occurrence = f"Keyword '{token.text}' found on page {page['page']}\n" \
#     #                         #  f"Context: ... {context} ..."
#     #             keyword_occurrences.append(occurrence)
    
#     for page in tender_documents:
#         doc = nlp(page['text'])
#         doc_text = page['text'].lower()  # Convert entire page text to lowercase
#         for phrase, category in keyword_category_map.items():
#             # Check for exact match of multi-word phrases or single words
#             if phrase in doc_text:
#                 relevant = True
#                 matched_categories.add(category)
#                 extracted_keywords.append(phrase)

#                 # Extract the context where the phrase appears
#                 start_pos = doc_text.find(phrase)
#                 context = doc_text[max(0, start_pos - 35):start_pos + len(phrase) + 35]

#                 occurrence = f"Keyword '{phrase}' found on page {page['page']}.\n"
#                 keyword_occurrences.append(occurrence)
                

                
#     logger.debug("Keyword mapping completed.")
                
#     # if relevant:
#     #     status = {
#     #         "Document Status": "Relevant",
#     #         "Categories": ", ".join(matched_categories)
#     #     }
#     # else:
#     #     status = {
#     #         "Document Status": "Not Relevant",
#     #         "Categories": None
#     #     }

#     # return status, keyword_occurrences
    
#     if relevant:
#         # Classify the tender based on the extracted keywords
#         classified_category = classify_tender(extracted_keywords, predefined_keywords)
        
#         print(classified_category)
        
#         status = {
#             "Document Status": "Relevant",
#             # "Categories": ", ".join(matched_categories) if classified_category != "ambiguous" else "Ambiguous"
#             "Categories": classified_category
#         }
        
#         print(status)
#     else:
#         status = {
#             "Document Status": "Not Relevant",
#             "Categories": None
#         }

#     return status, keyword_occurrences

def map_keywords_to_categories(tender_documents, predefined_keywords):
    logger.info("Mapping keywords to categories.")
    
    relevant = False
    matched_categories = set()
    keyword_occurrences = []
    extracted_keywords = []

    # Create a flat list of (category, keyword) tuples for easy lookup
    keyword_category_map = {}
    for category, keywords in predefined_keywords.items():
        for kw in keywords:
            keyword_category_map[kw.lower()] = category

    for page in tender_documents:
        doc_text = page['text'].lower()  # Convert entire page text to lowercase
        # Find keywords in the text using the match_keywords_with_punctuation function
        matches = match_keywords_with_punctuation(doc_text, keyword_category_map.keys())

        # Check if any matches were found
        if matches:
            relevant = True
            for match in matches:
                category = keyword_category_map[match.lower()]
                matched_categories.add(category)
                extracted_keywords.append(match)

                # Extract the context where the phrase appears
                start_pos = doc_text.find(match)
                context = doc_text[max(0, start_pos - 35):start_pos + len(match) + 35]

                occurrence = f"Keyword '{match}' found on page {page['page']}.\n"
                keyword_occurrences.append(occurrence)

    logger.debug("Keyword mapping completed.")
    
    if relevant:
        # Classify the tender based on the extracted keywords
        classified_category = classify_tender(extracted_keywords, predefined_keywords)
        
        print(classified_category)
        
        status = {
            "Document Status": "Relevant",
            "Categories": classified_category
        }
        
        print(status)
    else:
        status = {
            "Document Status": "Not Relevant",
            "Categories": None
        }

    return status, keyword_occurrences




