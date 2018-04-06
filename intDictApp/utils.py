

def convert_queryset_to_list_words(words):
    src_words = words.values_list('src_word', flat=True)
    src_words = list(src_words)
    target_words = words.values_list('target_word', flat=True)
    target_words = list(target_words)

    return src_words, target_words
