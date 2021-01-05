from setupui import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QApplication, QFileDialog, QSplashScreen
from PyQt5.QtCore import pyqtSignal, QTimer
import pyrebase, threading, re, os, gc, subprocess, random,time
import firebase_admin, xml.etree.ElementTree as ET
from firebase_admin import credentials, firestore
from scrypt import encrypt,decrypt
from reportlab.platypus import SimpleDocTemplate, Paragraph,Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors,pdfencrypt
from reportlab.lib.pdfencrypt import StandardEncryption


def file_exists():
	try:
		path = os.getcwd()
		dirs = os.listdir(path = path)
		if "config.xml" in dirs:
			tree = ET.parse("config.xml")
			root = tree.getroot()
			if str(root.tag) == "data" and str(root[0].tag) == "users" and str(root[0][0].tag) == "quote" :
				return True

		else:
			fopen = open("config.xml" , 'w')
			string = '''<data>\n<users>\n<quote>So many books, so little time. ― Frank Zappa</quote>\n
    <quote>Be yourself; everyone else is already taken. ― Oscar Wilde</quote>\n
    <quote>You only live once, but if you do it right, once is enough. ― Mae West</quote>\n
    <quote>Be the change that you wish to see in the world. ― Mahatma Gandhi</quote>\n
    <quote>In three words I can sum up everything I've learned about life: it goes on. ― Robert Frost</quote>\n
    <quote>A friend is someone who knows all about you and still loves you. ― Elbert Hubbard</quote>\n
    <quote>Always forgive your enemies; nothing annoys them so much. ― Oscar Wilde</quote>\n
    <quote>Live as if you were to die tomorrow. Learn as if you were to live forever. ― Mahatma Gandhi</quote>\n
    <quote>Every moment is a fresh beginning. – T.S Eliot</quote>\n
    <quote>Die with memories, not dreams. – Unknown</quote>\n
    <quote>Everything you can imagine is real. – Pablo Picasso</quote>\n
    <quote>Simplicity is the ultimate sophistication. – Leonardo da Vinci</quote>\n
    <quote>Whatever you do, do it well. – Walt Disney</quote>\n</users>\n</data>'''
			fopen.write(string)
			fopen.close()
			subprocess.check_call(["attrib" , "+H" , 'config.xml'])
			return True

	except:
		return False



def read_config():
	global total_user, quotes
	try:
		check = file_exists()
		if check:
			tree = ET.parse("config.xml")
			root = tree.getroot()
			if str(root.tag) == "data" and str(root[0].tag)=="users":
				for i in root:
					for j in i:
						if j.tag == "email":
							total_user.append(str(j.text))

						elif j.tag == "quote":
							quotes.append(str(j.text))

						else:
							os.remove("config.xml")
							file_exists()

	except:
		pass


current_user_credential = ""
quotes = list()
all_passwords = list()
total_user = list()
current_user = ""
user = None
authenticate = None
config = {"apiKey": "<Write Your Firebase Key>",
		    "authDomain": "",
			"databaseURL": "",
		    "projectId": "",
		    "storageBucket": "",
		    "messagingSenderId": "",
		    "appId": "",
		    "measurementId": ""}

firebase = pyrebase.initialize_app(config)
authenticate = firebase.auth()
config_db = {"type": "<Write Your Firebase Key>",
  "project_id": "",
  "private_key_id": "",
  "private_key": "",
  "client_email": "",
  "client_id": "",
  "auth_uri": "",
  "token_uri": "",
  "auth_provider_x509_cert_url": "",
  "client_x509_cert_url": ""

}
cred = credentials.Certificate(config_db)
firebase_admin.initialize_app(cred)
db = firestore.client()

class vault(QtCore.QObject):
	global ui, firebase, authenticate, db, current_user, user, total_user, current_user_credential
	#Signal
	login_signal = pyqtSignal(bool,str)
	signup_signal = pyqtSignal(bool,str)
	reset_password_signal = pyqtSignal(bool,str)
	save_password_signal = pyqtSignal(bool,str)
	message_cipher_signal = pyqtSignal(bool)
	pdf_created_signal = pyqtSignal(bool,tuple)

	def update_quote(self):
		global quotes
		try:
			random.shuffle(quotes)
			ui.statusbar_message.setText(random.choice(quotes))
		except:
			pass

	def message_cipher(self,msg):
		global current_user
		if msg:
			row_count = ui.tableWidget.rowCount()
			for i in range(row_count):
				checkbox = QtWidgets.QTableWidgetItem()
				checkbox.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
				checkbox.setCheckState(QtCore.Qt.Unchecked)
				ui.tableWidget.setItem(i , 3 , checkbox)

			ui.sync_decrypt_label.hide()
			ui.statusbar_message.setText("Welcome {0}".format(current_user.partition('@')[0].capitalize()))

		else:
			ui.statusbar_message.setText("Decrypting data...")
			ui.sync_decrypt_label.show()
			icon1 = QtGui.QMovie(":/resources/resources/check.gif")
			ui.sync_decrypt_label.setMovie(icon1)
			icon1.start()

	def login_message(self, msg, type):
		message = QMessageBox(MainWindow)
		ui.label_10.hide()
		ui.pushButton.setDisabled(False)
		QApplication.restoreOverrideCursor()
		if msg:
			ui.lineEdit.clear()
			ui.userpassword_lineedit.clear()
			ui.stackedWidget.setCurrentWidget(ui.page_3)
			ui.menubar.show()
			ui.lineEdit_3.setFocus()

		else:
			if type == "<class 'requests.exceptions.ConnectionError'>":
				message.setIcon(QMessageBox.Critical)
				message.setText("Network Not Available")
				message.setWindowTitle("Retry Error No 11004")
				message.exec_()

			elif type == "<class 'requests.exceptions.HTTPError'>":
				message.setIcon(QMessageBox.Warning)
				message.setText("Email or Password is Incorrect")
				message.setWindowTitle("Retry Error No 400")
				message.exec_()

			else:
				message.setIcon(QMessageBox.Critical)
				message.setText("Something Went Wrong")
				message.setWindowTitle("Error")
				message.exec_()

	def signup_message(self, msg, type):
		message = QMessageBox(MainWindow)
		ui.label_11.hide()
		ui.ok_button_3.setDisabled(False)
		QApplication.restoreOverrideCursor()
		if msg:
			ui.menubar.show()
			ui.name_lineedit.clear()
			ui.password_lineedit.clear()
			ui.lineEdit_2.clear()
			ui.stackedWidget.setCurrentWidget(ui.page_3)
			ui.lineEdit_3.setFocus()
			message.setIcon(QMessageBox.Information)
			message.setText("Account Created Successfully")
			message.setWindowTitle("Welcome")
			message.exec_()
			ui.statusbar_message.setText("Welcome {0}".format(type.partition('@')[0].capitalize()))

		else:
			if type == "<class 'requests.exceptions.ConnectionError'>":
				message.setIcon(QMessageBox.Critical)
				message.setText("Network Not Available")
				message.setWindowTitle("Retry Error No 11004")
				message.exec_()

			elif type == "<class 'requests.exceptions.HTTPError'>":
				message.setIcon(QMessageBox.Warning)
				message.setText("Email or Password is Incorrect")
				message.setWindowTitle("Retry Error No 400")
				message.exec_()

			else:
				message.setIcon(QMessageBox.Critical)
				message.setText("Something Went Wrong")
				message.setWindowTitle("Error")
				message.exec_()

	def reset_password_message(self, msg, type):
		message = QMessageBox(MainWindow)
		ui.pushButton_3.setDisabled(False)
		QApplication.restoreOverrideCursor()
		if msg:
			message.setIcon(QMessageBox.Information)
			message.setText("Password Reset mail sended at {0}".format(type))
			message.setWindowTitle("Check Mailbox")
			message.exec_()

		else:
			if type == "<class 'requests.exceptions.ConnectionError'>":
				message.setIcon(QMessageBox.Critical)
				message.setText("Network Not Available")
				message.setWindowTitle("Retry Error No 11004")
				message.exec_()

			elif type == "<class 'requests.exceptions.HTTPError'>":
				message.setIcon(QMessageBox.Critical)
				message.setText("No Account exists with this Email")
				message.setWindowTitle("Not Found")
				message.exec_()

			else:
				message.setIcon(QMessageBox.Critical)
				message.setText("Something Went Wrong")
				message.setWindowTitle("Error")
				message.exec_()

	def save_password_message(self, msg, type):
		message = QMessageBox(MainWindow)
		ui.menuOptions.setDisabled(False)
		ui.encryptdata_button.setDisabled(False)
		QApplication.restoreOverrideCursor()
		if msg:
			checkbox = QtWidgets.QTableWidgetItem()
			checkbox.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
			checkbox.setCheckState(QtCore.Qt.Unchecked)
			ui.tableWidget.setItem(ui.tableWidget.rowCount()-1 , 3 , checkbox)
			ui.label_12.hide()
			ui.lineEdit_3.setFocus()
			ui.statusbar_message.setText("Information Synced with Cloud")
			message.setIcon(QMessageBox.Information)
			message.setText("Information Synced with Cloud")
			message.setWindowTitle("Done")
			message.exec_()

		else:
			ui.statusbar_message.setText("Something Went Wrong")
			message.setIcon(QMessageBox.Critical)
			message.setText("Something Went Wrong")
			message.setWindowTitle("Error")
			message.exec_()
			ui.lineEdit_3.setFocus()

	def pdf_message(self,msg,location):
		if msg:
			message = QMessageBox(MainWindow)
			message.setIcon(QMessageBox.Information)
			message.setText("PDF Created at location - {0} with your master password as Password".format(location[0]))
			message.setWindowTitle("PDF Created")
			message.exec_()
		else:
			message = QMessageBox(MainWindow)
			message.setIcon(QMessageBox.Warning)
			message.setText("Unable to create PDF at this location - {0}".format(location[0]))
			message.setWindowTitle("Error")
			message.exec_()

	def __init__(self):
		global total_user
		super().__init__()
		self.timer = QTimer()
		self.timer.timeout.connect(self.logout)
		self.timer.start(2700000)
		# Signal Connect
		self.login_signal.connect(self.login_message)
		self.signup_signal.connect(self.signup_message)
		self.reset_password_signal.connect(self.reset_password_message)
		self.save_password_signal.connect(self.save_password_message)
		self.message_cipher_signal.connect(self.message_cipher)
		self.pdf_created_signal.connect(self.pdf_message)
		completer = QtWidgets.QCompleter(total_user)
		completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
		completer.setCaseSensitivity(False)
		ui.lineEdit.setCompleter(completer)

	def encrypt_password(self,password):
		global current_user
		return encrypt(password,current_user,maxtime = 0.5)

	def decrypt_password(self,password):
		global current_user
		return decrypt(password,current_user)



	def thread_login_fun(self,email,password):
		global current_user, user, total_user, all_passwords, current_user_credential
		try:
			user = authenticate.sign_in_with_email_and_password(email , password)
			current_user = email
			current_user_credential = password
			self.login_signal.emit(True , email)
			try:
				user_ref = db.collection("{0}".format(current_user))
				docs = user_ref.stream()
				self.message_cipher_signal.emit(False)
				for doc in docs:
					temp = list()
					temp.clear()
					temp.append(str(doc.id))
					temp_var = doc.to_dict()
					name = self.decrypt_password(temp_var["Name"])
					password = self.decrypt_password(temp_var["Password"])
					temp_var["Name"] = name
					temp_var["Password"] = password
					temp.append(temp_var)
					all_passwords.append(temp)

				ui.tableWidget.setRowCount(len(all_passwords))
				for i in range(len(all_passwords)):
					count = 0
					for k in all_passwords[i][1].keys():
						if k == "Password":
							count = 2
						elif k == "Account Name":
							count = 0
						else:
							count = 1
						ui.tableWidget.setItem(i , count , QtWidgets.QTableWidgetItem(all_passwords[i][1][k]))

				header = ui.tableWidget.horizontalHeader()
				header.setSectionResizeMode(0 , QtWidgets.QHeaderView.ResizeToContents)
				header.setSectionResizeMode(1 , QtWidgets.QHeaderView.ResizeToContents)
				header.setSectionResizeMode(2 , QtWidgets.QHeaderView.ResizeToContents)
				header.setSectionResizeMode(3 , QtWidgets.QHeaderView.ResizeToContents)

			except:
				pass


			try:
				check = file_exists()
				if check and (email not in total_user):
					tree = ET.parse("config.xml")
					root = tree.getroot()
					new_email = ET.SubElement(root[0], "email")
					new_email.text = "{0}".format(email)
					tree.write('config.xml')
					total_user.append(email)

			except:
				pass

			self.message_cipher_signal.emit(True)

		except:
			type = sys.exc_info()[0]
			type = str(type)
			self.login_signal.emit(False, type)


	def login(self):
		reg ="^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"
		message = QMessageBox(MainWindow)
		email = ui.lineEdit.text().strip()
		password = ui.userpassword_lineedit.text().strip()
		if email != '' and password != '' and len(password)>=6 and re.search(reg, email):
			email = str(email)
			password = str(password)
			self.thread_var_login = threading.Thread(target = self.thread_login_fun, args = (email,password,), daemon = True).start()
			ui.pushButton.setDisabled(True)
			QApplication.setOverrideCursor(QtCore.Qt.BusyCursor)
			ui.label_10.show()
			icon1 = QtGui.QMovie(":/resources/resources/check.gif")
			ui.label_10.setMovie(icon1)
			icon1.start()
		else:
			message.setIcon(QMessageBox.Warning)
			message.setText("Enter data correctly!")
			message.setWindowTitle("Retry")
			message.exec_()


	def thread_signup_fun(self, email, password):
		global current_user, user, total_user, current_user_credential
		try:
			user = authenticate.create_user_with_email_and_password(email, password)
			current_user = email
			current_user_credential = password
			self.signup_signal.emit(True, email)
			try:
				check = file_exists()
				if check and (email not in total_user):
					tree = ET.parse("config.xml")
					root = tree.getroot()
					new_email = ET.SubElement(root[0], "email")
					new_email.text = "{0}".format(email)
					tree.write('config.xml')
					total_user.append(email)

			except:
				pass

		except:
			type = sys.exc_info()[0]
			type = str(type)
			self.signup_signal.emit(False , type)


	def signup(self):
		reg = "^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"
		message = QMessageBox(MainWindow)
		email = ui.name_lineedit.text().strip()
		password = ui.password_lineedit.text().strip()
		confirm_password = ui.lineEdit_2.text().strip()
		if email!='' and password!='' and password==confirm_password and len(password)>=6 and re.search(reg, email):
			email = str(email)
			password = str(password)
			self.thread_var_signup = threading.Thread(target = self.thread_signup_fun, args = (email,password,), daemon = True).start()
			ui.ok_button_3.setDisabled(True)
			QApplication.setOverrideCursor(QtCore.Qt.BusyCursor)
			ui.label_11.show()
			icon1 = QtGui.QMovie(":/resources/resources/check.gif")
			ui.label_11.setMovie(icon1)
			icon1.start()

		else:
			message.setIcon(QMessageBox.Warning)
			message.setText("Enter data correctly!")
			message.setWindowTitle("Retry")
			message.exec_()

	def thread_reset_password_fun(self, email):
		global authenticate
		try:
			authenticate.send_password_reset_email(email)
			self.reset_password_signal.emit(True, email)
		except:
			type = sys.exc_info()[0]
			type = str(type)
			self.reset_password_signal.emit(False, type)


	def reset_password(self):
		message = QMessageBox(MainWindow)
		reg = "^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"
		input_dialog = QInputDialog()
		(email, ok) = input_dialog.getText(MainWindow, "Reset Password", "Enter valid email", QtWidgets.QLineEdit.Normal, flags = (QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowStaysOnTopHint))
		email = str(email)
		if ok and email!='' and re.search(reg, email):
			thread_var_reset_password = threading.Thread(target = self.thread_reset_password_fun, args=(email,), daemon = True).start()
			ui.pushButton_3.setDisabled(True)
			QApplication.setOverrideCursor(QtCore.Qt.BusyCursor)

		elif ok:
			message.setIcon(QMessageBox.Warning)
			message.setText("Enter data correctly!")
			message.setWindowTitle("Retry")
			message.exec_()

		else:
			pass

	def thread_save_password_fun(self, account_name, user_name, password):
		global current_user,all_passwords,db
		try:
			name = self.encrypt_password(user_name)
			pass_code = self.encrypt_password(password)
			ui.statusbar_message.setText("Establishing connection with server...")
			dict_upload = {"Account Name": account_name , "Name": name , "Password": pass_code}
			dict = {"Account Name": account_name , "Name": user_name , "Password": password}
			doc = db.collection("{0}".format(current_user)).document()
			temp_var = doc.id
			doc.set(dict_upload)
			ui.lineEdit_3.clear()
			ui.lineEdit_4.clear()
			ui.lineEdit_5.clear()
			ui.tableWidget.insertRow(ui.tableWidget.rowCount())
			ui.tableWidget.setItem(ui.tableWidget.rowCount()-1, 0,QtWidgets.QTableWidgetItem(account_name))
			ui.tableWidget.setItem(ui.tableWidget.rowCount()-1, 1,QtWidgets.QTableWidgetItem(user_name))
			ui.tableWidget.setItem(ui.tableWidget.rowCount()-1, 2,QtWidgets.QTableWidgetItem(password))
			temp = list()
			temp.append(str(temp_var))
			temp.append(dict)
			all_passwords.append(temp)
			header = ui.tableWidget.horizontalHeader()
			header.setSectionResizeMode(0 , QtWidgets.QHeaderView.ResizeToContents)
			header.setSectionResizeMode(1 , QtWidgets.QHeaderView.ResizeToContents)
			header.setSectionResizeMode(2 , QtWidgets.QHeaderView.ResizeToContents)
			self.save_password_signal.emit(True , current_user)

		except:
			type = sys.exc_info()
			type = str(type)
			self.save_password_signal.emit(False, type)

	def save_password(self):
		message = QMessageBox(MainWindow)
		account_name = ui.lineEdit_3.text().strip()
		user_name = ui.lineEdit_4.text().strip()
		password = ui.lineEdit_5.text().strip()
		if account_name!='' and user_name!='' and password!='':
			self.thread_var_save_password = threading.Thread(target = self.thread_save_password_fun, args = (account_name, user_name, password, ), daemon = True).start()
			ui.encryptdata_button.setDisabled(True)
			QApplication.setOverrideCursor(QtCore.Qt.BusyCursor)
			ui.statusbar_message.setText("Encrypting data...")
			ui.menuOptions.setDisabled(True)
			ui.label_12.show()
			icon1 = QtGui.QMovie(":/resources/resources/check.gif")
			ui.label_12.setMovie(icon1)
			icon1.start()

		else:
			message.setIcon(QMessageBox.Warning)
			message.setText("Enter data correctly!")
			message.setWindowTitle("Retry")
			message.exec_()


	def logout(self):
		global current_user, all_passwords, quotes, current_user_credential
		authenticate.currentUser = None
		current_user = ""
		current_user_credential = ""
		all_passwords.clear()
		ui.tableWidget.clearContents()
		ui.tableWidget.setRowCount(0)
		ui.stackedWidget.setCurrentWidget(ui.page)
		ui.statusbar_message.clear()
		ui.menubar.hide()
		ui.lineEdit.setFocus()
		self.update_quote()

	def show_password_login(self):
		if ui.action.isChecked():
			view = QtGui.QIcon(QtGui.QPixmap(":/resources/resources/invisible.png"))
			ui.action.setIcon(view)
			ui.userpassword_lineedit.setEchoMode(QtWidgets.QLineEdit.Normal)
			ui.password_lineedit.setEchoMode(QtWidgets.QLineEdit.Normal)
			ui.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Normal)
			ui.lineEdit_5.setEchoMode(QtWidgets.QLineEdit.Normal)
		else:
			view = QtGui.QIcon(QtGui.QPixmap(":/resources/resources/eye-close-up.png"))
			ui.action.setIcon(view)
			ui.userpassword_lineedit.setEchoMode(QtWidgets.QLineEdit.Password)
			ui.password_lineedit.setEchoMode(QtWidgets.QLineEdit.Password)
			ui.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
			ui.lineEdit_5.setEchoMode(QtWidgets.QLineEdit.Password)

	def auto_capital(self):
		edit = ui.lineEdit_3.text()
		ui.lineEdit_3.setText(str(edit.title()))

	def lineEdit_color(self):
		reg = "^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"
		text = ui.lineEdit.text().strip()
		if re.search(reg,text):
			ui.lineEdit.setStyleSheet("color: rgb(0,170,0)")

		elif text=='':
			ui.lineEdit.setStyleSheet("color: rgb(0,0,0)")
		else:
			ui.lineEdit.setStyleSheet("color: rgb(255,0,0)")

	def name_lineedit_color(self):
		reg = "^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$"
		text = ui.name_lineedit.text().strip()
		if re.search(reg , text):
			ui.name_lineedit.setStyleSheet("color: rgb(0,170,0)")

		elif text=='':
			ui.name_lineedit.setStyleSheet("color: rgb(0,0,0)")

		else:
			ui.name_lineedit.setStyleSheet("color: rgb(255,0,0)")

	def developer(self):
		message = QMessageBox(MainWindow)
		message.setIcon(QMessageBox.Information)
		message.setText("This Application is free to distribute!")
		message.setInformativeText("")
		message.setWindowTitle("Application Developed by Bhargav Ditani")
		message.exec_()

	def thread_delete_user_account_fun(self):
		global current_user , all_passwords
		try:
			row_count = ui.tableWidget.rowCount()
			if row_count:
				for i in range(row_count):
					item = ui.tableWidget.item(i , 3).checkState()
					if item:
						user_ref = db.collection("{0}".format(current_user)).document(all_passwords[i][0]).delete()
						all_passwords[i][0] = -1
						ui.tableWidget.item(i,3).setCheckState(QtCore.Qt.Unchecked)
						ui.tableWidget.setRowHidden(i, True)
			ui.sync_decrypt_label.hide()
		except:
			ui.sync_decrypt_label.hide()

	def delete_user_account(self):
		try:
			ui.sync_decrypt_label.show()
			icon1 = QtGui.QMovie(":/resources/resources/check.gif")
			ui.sync_decrypt_label.setMovie(icon1)
			icon1.start()
			self.thread_var_delete_user_account = threading.Thread(target = self.thread_delete_user_account_fun, daemon = True).start()
		except:
			pass

	def thread_export_fun(self,List,location):
		global current_user,current_user_credential
		try:
			pass_code = StandardEncryption("{0}".format(current_user_credential))
			if str(location[0][-1]) == 'f' and str(location[0][-2]) == 'd' and str(location[0][-3]) == 'p':
				my_doc = SimpleDocTemplate("{0}".format(location[0]),encrypt = pass_code, pagesize = A4 , topMargin = 1 * inch ,
			                           leftMargin = 1 * inch ,
			                           rightMargin = 1 * inch ,
			                           bottomMargin = 1 * inch)
			else:
				my_doc = SimpleDocTemplate("{0}.pdf".format(location[0]) , encrypt = pass_code , pagesize = A4 ,
				                           topMargin = 1 * inch ,
				                           leftMargin = 1 * inch ,
				                           rightMargin = 1 * inch ,
				                           bottomMargin = 1 * inch)
			sample_style_sheet = getSampleStyleSheet()
			flowables = []
			custom_heading_style = sample_style_sheet['Heading1']
			custom_heading_style.fontName = "Helvetica"
			custom_heading_style.fontSize = 25
			custom_heading_style.spaceAfter = 20
			custom_heading_style.textColor = colors.green
			paragraph_1 = Paragraph("Password Vault" , custom_heading_style)
			custom_body_style = sample_style_sheet['BodyText']
			custom_body_style.fontName = "Helvetica"
			custom_body_style.fontSize = 15
			custom_body_style.spaceAfter = 20
			paragraph_2 = Paragraph("Passwords For Account - <i>{0}</i>".format(current_user) , custom_body_style)
			tab = Table(List)
			tab_style = TableStyle([
				('GRID' , (0 , 0) , (-1 , -1) , 0.25 , colors.black) ,
				('BOX' , (0 , 0) , (-1 , -1) , 0.25 , colors.black , None , (2 , 2 , 1)) ,
				('BACKGROUND' , (2 , 0) , (2 , 0) , colors.darkorange) ,
				('BACKGROUND' , (0 , 0) , (0 , 0) , colors.azure) ,
				('BACKGROUND' , (1 , 0) , (1 , 0) , colors.beige) ,
				('BACKGROUND' , (3 , 0) , (3 , 0) , colors.aquamarine) ,
				('FONTSIZE' , (0 , 0) , (-1 , -1) , 12) ,
				('INNERGRID' , (0 , 0) , (-1 , -1) , 0.25 , colors.black) ,
				('ALIGN' , (1 , 1) , (-1 , -1) , 'CENTER')
			])
			tab.setStyle(tab_style)
			flowables.append(paragraph_1)
			flowables.append(paragraph_2)
			flowables.append(tab)
			my_doc.build(flowables)
			self.pdf_created_signal.emit(True,location)

		except:
			type = sys.exc_info()
			type = str(type)
			self.pdf_created_signal.emit(False , location)


	def export(self):
		global current_user, all_passwords
		message = QMessageBox(MainWindow)
		List = [["Sr No.","Account Name" , "User Name" , "Password"]]
		if len(all_passwords) != 0:
			count = 1
			for i in range(len(all_passwords)):
				if all_passwords[i][0] != -1:
					temp = list()
					temp.clear()
					account_name = str(all_passwords[i][1]["Account Name"])
					user_name = str(all_passwords[i][1]["Name"])
					password = str(all_passwords[i][1]["Password"])
					temp.append(str(count))
					temp.append(account_name)
					temp.append(user_name)
					temp.append(password)
					List.append(temp)
					count += 1

			if len(List) != 1:
				dialog = QFileDialog()
				dialog.setFileMode(QFileDialog.AnyFile)
				filter = "pdf(*.pdf)"
				path = os.getcwd()
				location = dialog.getSaveFileName(dialog , filter = filter)
				if location[0] != '':
					self.thread_var_export = threading.Thread(target=self.thread_export_fun,args = (List,location,), daemon = True).start()

			else:
				message.setIcon(QMessageBox.Information)
				message.setText("Nothing To Export!")
				message.setWindowTitle("No Export")
				message.exec_()

		else:
			message.setIcon(QMessageBox.Information)
			message.setText("Nothing To Export!")
			message.setWindowTitle("No Export")
			message.exec_()


if __name__ == "__main__":
	thread_var_read_config = threading.Thread(target = read_config).start()
	import sys
	gc.enable()
	app = QtWidgets.QApplication(sys.argv)
	splash_pix = QtGui.QPixmap(':resources/resources/splash.png')
	splash = QSplashScreen(splash_pix , QtCore.Qt.WindowStaysOnTopHint)
	splash.setMask(splash_pix.mask())
	splash.show()
	app.processEvents()
	MainWindow = QtWidgets.QMainWindow()
	ui = Ui_MainWindow()
	ui.setupUi(MainWindow)
	time.sleep(2)
	object = vault()
	ui.pushButton.clicked.connect(object.login)
	ui.ok_button_3.clicked.connect(object.signup)
	ui.pushButton_2.clicked.connect(lambda: ui.stackedWidget.setCurrentWidget(ui.page_2) or ui.name_lineedit.setFocus())
	ui.pushButton_4.clicked.connect(lambda: ui.stackedWidget.setCurrentWidget(ui.page)or ui.lineEdit.setFocus())
	ui.pushButton_3.clicked.connect(object.reset_password)
	ui.encryptdata_button.clicked.connect(object.save_password)
	ui.getdata_button.clicked.connect(lambda: ui.stackedWidget.setCurrentWidget(ui.page_4))
	ui.pushButton_6.clicked.connect(lambda: ui.stackedWidget.setCurrentWidget(ui.page_3) or ui.lineEdit_3.setFocus())
	ui.actiondelete.triggered.connect(object.delete_user_account)
	ui.actionLog_out.triggered.connect(object.logout)
	ui.actionExit.triggered.connect(lambda: sys.exit())
	ui.action.triggered.connect(object.show_password_login)
	ui.lineEdit_3.textChanged.connect(object.auto_capital)
	ui.lineEdit.textChanged.connect(object.lineEdit_color)
	ui.name_lineedit.textChanged.connect(object.name_lineedit_color)
	ui.about_button.clicked.connect(object.developer)
	ui.actionexport.triggered.connect(object.export)
	object.update_quote()
	ui.lineEdit.setFocus()
	splash.finish(MainWindow.show())
	sys.exit(app.exec_())
