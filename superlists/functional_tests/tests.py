from django.test import LiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException

import time

MAX_WAIT = 10


class NewVisitorTest(LiveServerTestCase):

	def setUp(self):
		self.browser = webdriver.Firefox()

	def tearDown(self):
		self.browser.quit()

	def wait_for_row_in_list_table(self, row_text):
		start_time = time.time()

		while True:
			try:
				table = self.browser.find_element_by_id('id_list_table')
				rows = table.find_elements_by_tag_name('tr')
				self.assertIn(row_text, [row.text for row in rows])
				return
			except (AssertionError, WebDriverException) as e:
				if time.time() - start_time > MAX_WAIT:
					raise e
				time.sleep(0.5)

	def test_can_start_a_list_for_one_user(self):

		"""
		Edir ouviu falar de uma nova aplicação online interessante
		para lista de tarefas. Ela decide verificar sua homepage
		"""
		self.browser.get(self.live_server_url)

		"""
		Ela percebe que o título da página e o cabeçalho
		mencionam listas de tarefas (to-do)
		"""
		self.assertIn('To-Do', self.browser.title)
		header_text = self.browser.find_element_by_tag_name('h1').text
		self.assertIn('To-Do', header_text)

		"""
		Ela é convidada a inserir um item de tarefa imediatamente
		"""
		inputbox = self.browser.find_element_by_id('id_new_item')
		self.assertEqual(
			inputbox.get_attribute('placeholder'),
			'Enter a to-do item'
			)

		"""
		Ela digita "Buy peacock feathers" (comprar penas de pavão)
		em uma caixa de texto (o hobby de Edith é fazer iscas de 
		pesca com fly)
		"""
		inputbox.send_keys('Buy peacock feathers')

		"""
		Quando ela tecla enter, a página é atualizada, e agora
		a página lista "i: Buy peacock feathers" como um item em uma
		lista de tarefas
		"""	
		inputbox.send_keys(Keys.ENTER)
		self.wait_for_row_in_list_table('1: Buy peacock feathers')

		"""
		Ainda contina havendo uma caixa de texto convidando-a a 
		acrescentar outro item. Ela insere "Use peacock feathers to make a fly"
		(Usar penas de pavão para fazer um fly - Edit é bem metódica)
		"""
		inputbox = self.browser.find_element_by_id('id_new_item')
		inputbox.send_keys('Use peacock feathers to make a fly')
		inputbox.send_keys(Keys.ENTER)
		
		"""
		A página é atualizada novamente e agora mostra os dois itens
		em sua lista
		"""
		self.wait_for_row_in_list_table('1: Buy peacock feathers')
		self.wait_for_row_in_list_table('2: Use peacock feathers to make a fly')

		# satisfeita ela vai dormir

		# self.fail('Finish the test!')

	def test_multiple_users_can_start_lists_at_different_urls(self):
		# Edith starts a new to-do list
		self.browser.get(self.live_server_url)
		inputbox = self.browser.find_element_by_id('id_new_item')
		inputbox.send_keys('Buy peacock feathers')
		inputbox.send_keys(Keys.ENTER)
		self.wait_for_row_in_list_table('1: Buy peacock feathers')

		# She notices that her list has a unique URL
		edith_list_url = self.browser.current_url
		self.assertRegex(edith_list_url, '/lists/.+')

		# Now a new user, Francis, comes along to the site

		## We use a new browser session to make sure that no
		## information of Edit's is commig through from cookies, etc
		self.browser.quit()
		self.browser = webdriver.Firefox()

		# Francis visits the home page. There is no sign
		# of Edith's list
		self.browser.get(self.live_server_url)
		page_text = self.browser.find_element_by_tag_name('body').text
		self.assertNotIn('Buy peacock feathers', page_text)
		self.assertNotIn('make a fly', page_text)

		# Francis starts a new list by entering a new item.
		# He is less interesting that Edith...
		inputbox = self.browser.find_element_by_id('id_new_item')
		inputbox.send_keys('Buy milk')
		inputbox.send_keys(Keys.ENTER)
		self.wait_for_row_in_list_table('1: Buy milk')

		# Francis gets his own unique URL
		francis_list_url = self.browser.current_url
		self.assertRegex(francis_list_url, '/lists/.+')
		self.assertNotEqual(francis_list_url, edith_list_url)

		# Again, there is no trace of Edith's list
		page_text = self.browser.find_element_by_tag_name('body').text
		self.assertNotIn('Buy peacock feathers', page_text)
		self.assertIn('Buy milk')

		# Satisfied, they both go back to sleep
