class BookLoader:
	def __init__(self):
		self.__path = ""

	def set_path(self, path: str):
		self.__path = path

	def read(self):
		with open(self.__path, "r") as file:
			return file.read()

	def split_into_given_sb(self, number: int):
		whole_text = self.read()
		split_text = [whole_text[i:i + number] for i in range(0, len(whole_text), number)]
		return split_text


class UI:

	@staticmethod
	def show_books_list(books_data: list[dict]):
		result = ""
		for dictionary in books_data:
			result = result + f"{dictionary["index"]}. {dictionary["name"]}. Автор: {dictionary["author"]} \n"
		return result
