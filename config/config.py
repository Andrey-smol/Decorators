import os.path


class Config_:
    __PATH_FILE_LOG = os.path.join(os.getcwd(), 'main.log')
    __PATH_FILE_LOG_DIR = os.path.join(os.getcwd(), 'files', 'main.log')

    __URL = 'https://habr.com/ru/articles/'
    __NUMBER_PAGES_VIEWING = 5
    __KEYWORDS = ['дизайн', 'фото', 'web', 'python']

    @classmethod
    def get_path_file_log(cls):
        return cls.__PATH_FILE_LOG

    @classmethod
    def get_path_file_log_into_dir(cls):
        return cls.__PATH_FILE_LOG_DIR

    @classmethod
    def get_number_pages(cls) -> int:
        return cls.__NUMBER_PAGES_VIEWING

    @classmethod
    def get_search_words(cls) -> list:
        return cls.__KEYWORDS

    @classmethod
    def get_url(cls):
        return cls.__URL
