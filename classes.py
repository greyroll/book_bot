class BookLoader:
	def __init__(self, path: str):
		self.path = path

	def read(self):
		with open(self.path, "r") as file:
			return file.read()

	def split_into_500_sb(self):
		whole_text = self.read()
		split_text = [whole_text[i:i + 500] for i in range(0, len(whole_text), 500)]
		return split_text


class UI:

	@staticmethod
	def show_books_list(books_data: list[dict]):
		result = ""
		for dictionary in books_data:
			result = result + f"{dictionary["index"]}. {dictionary["name"]}. Автор: {dictionary["author"]} \n"
		return result
