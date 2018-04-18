def convert_queryset_to_list_words(words):
    src_words = words.values_list('src_word', flat=True)
    src_words = list(src_words)
    target_words = words.values_list('target_word', flat=True)
    target_words = list(target_words)

    return src_words, target_words


def convert_queryset_to_list_languages(src_languages, target_languages):
    src_languages = src_languages.values_list('name', flat=True)
    src_languages_lst = list(src_languages)
    target_languages = target_languages.values_list('name', flat=True)
    target_languages_lst = list(target_languages)

    return src_languages_lst, target_languages_lst


def find_highest_request_idx(keys):

    high_idx = 0

    for item in keys:
        if item.startswith("left_field"):
            num = int(item[10:])
            if num > high_idx:
                high_idx = num

    return high_idx
