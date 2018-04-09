from random import shuffle


class Config:
    """
    Using for exchanging data between views
    """
    current_category = None  # Query set
    current_category_id = 0
    current_set = None  # Query set
    current_set_id = None
    shuffled_idxes = None
    current_word_idx = 0
    size = 0
    corr_ans_num = 0
    curr_corr_ans = ''
    answers_list = []
    is_check_clicked = False

    def create_shuffle_list(self, size):

        self.size = size
        self.answers_list = [""] * size
        self.shuffled_idxes = list(range(size))
        shuffle(self.shuffled_idxes)

    def clean_up(self):
        self.shuffled_idxes = None
        self.current_word_idx = 0
        self.size = 0
        self.corr_ans_num = 0
        self.curr_corr_ans = ''
        self.answers_list = []
        self.is_check_clicked = False

    def assign_val_to_answers_list(self, idx, value):
        self.answers_list[idx] = value
