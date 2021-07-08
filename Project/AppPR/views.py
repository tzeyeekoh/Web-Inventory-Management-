from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.db import connection
from django.http import JsonResponse
import datetime

# Create your views here.
def index(request):
	try:
		if request.session['usertype'] == 'Staff':
			return render(request,'AppPR/staffportal.html')
		elif request.session['usertype'] == 'Student':
			return render(request,'AppPR/studentportal.html')
		else: 
			request.session['usertype'] = 'Anon'
			return render(request, 'AppPR/index.html')
	except KeyError:
		request.session['usertype'] = 'Anon'
		return render(request, 'AppPR/index.html')

def closeportal(request):
	request.session['usertype'] = 'Anon'
	return HttpResponseRedirect('/AppPR')

def login(request):
	##Retreive Input
	email = request.GET.get('email')
	password = request.GET.get('password')

	try:
		query ="""SELECT m.role FROM members m
				WHERE email = '%s' AND password = '%s' """ % (email, password)
		c = connection.cursor()
		c.execute(query)

		role = c.fetchall()
		user = role[0][0]
	except IndexError:
		return render(request, 'AppPR/error.html')

	if user == 'Staff':
		request.session['usertype'] = user
		return HttpResponseRedirect('/AppPR')
	elif user == 'Student':
		request.session['usertype'] = user
		return HttpResponseRedirect('/AppPR')
	
def requests(request):
	## Query
	query ="""DROP VIEW IF EXISTS view_requests;
			CREATE VIEW view_requests AS
			SELECT r.ReqID, m.first_name ||' '||m.last_name AS name, r.request_date, r.item, r.model_number, r.quantity, r.vendor, r.unit_price, r.ship_price, (CASE 
																									 WHEN r.receive_date IS NULL
																									 AND r.ReqID NOT IN (
																									 SELECT a.ReqID FROM approval a)
																									 THEN CAST('Pending Approval'AS VARCHAR(64))
																									 WHEN r.receive_date IS NULL THEN CAST('Pending Delivery' AS VARCHAR(64))
																									 ELSE CAST('Received: ' || r.receive_date AS VARCHAR(64))
																									 END) AS status
			FROM requests r, members m
			WHERE r.requestor = m.email
			ORDER BY request_date DESC;
			SELECT * FROM view_requests;"""
	# The connection object.
	c = connection.cursor()
	# Execute query by connection object
	c.execute(query)
	# Fetch all the rows. fetchall() returns a list of tuples.
	requests = c.fetchall()
	requests_dict = {'requests': requests}
	return render(request,'AppPR/requests.html',requests_dict)
	
def members(request):
	## Query
	query ="SELECT m.first_name||' '||m.last_name as full_name, m.email, m.role FROM members m ORDER BY full_name"
	# The connection object.
	c = connection.cursor()
	# Execute query by connection object
	c.execute(query)
	# Fetch all the rows. fetchall() returns a list of tuples.
	results = c.fetchall()
	result_dict = {'records': results}
	return render(request,'AppPR/members.html',result_dict)

def inventory(request):
	## Query
	query ="""DELETE FROM inventory;
			INSERT INTO inventory(item, model_number, inv_quantity)
			SELECT item, model_number, SUM(quantity) AS inv_quantity FROM requests
			WHERE receive_date IS NOT NULL
			GROUP BY (item, model_number);
			SELECT * FROM inventory
			ORDER BY item;"""
	# The connection object.
	c = connection.cursor()
	# Execute query by connection object
	c.execute(query)
	# Fetch all the rows. fetchall() returns a list of tuples.
	inv = c.fetchall()

	expense_query = """SELECT SUM(r.ship_price)+SUM(r.quantity * r.unit_price) AS expense
					FROM requests r
					WHERE EXISTS(
					SELECT a.ReqID FROM approval a
					WHERE a.ReqID = r.ReqID);"""
	e = connection.cursor()
	e.execute(expense_query)
	exp = e.fetchall()

	inv_value_query = """SELECT SUM(r.quantity * r.unit_price) AS expense
						FROM requests r
						WHERE receive_date IS NOT NULL;"""
	iv = connection.cursor()
	iv.execute(inv_value_query)
	inv_value = iv.fetchall()

	##Run Exp Chart
	expChart(request)

	return render(request, 'AppPR/inventory.html', {'records': inv, 'expense': exp, 'inv_value': inv_value})

def expChart(request):
	## Query
	query ="""SELECT to_char(a.approve_date, 'YYYY - MM'), SUM((r.unit_price * r.quantity) + r.ship_price) AS total_cost FROM approval a, requests r
			WHERE a.ReqID = r.ReqID
			GROUP BY to_char(a.approve_date, 'YYYY - MM')
			ORDER BY to_char(a.approve_date, 'YYYY - MM') DESC"""
	# The connection object.
	c = connection.cursor()
	# Execute query by connection object
	c.execute(query)
	# Fetch all the rows. fetchall() returns a list of tuples.
	expc = c.fetchall()
	return JsonResponse(expc, safe=False)

def newReq(request):

	##Retrieve new ReqID
	newReqID = "SELECT MAX(ReqID)+1 As newReqID FROM requests"
	# The connection object.
	r = connection.cursor()
	# Execute query by connection object
	r.execute(newReqID)

	newReqID = r.fetchall()
	

	##Retrieve input
	ReqID = newReqID[0][0]
	req_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	item = request.GET.get('item')
	model_number = request.GET.get('model_number')
	quantity = request.GET.get('quantity')
	vendor = request.GET.get('vendor')
	unit_price = request.GET.get('unit_price')
	ship_price = request.GET.get('ship_price')
	requestor = request.GET.get('requestor')
	## Query
	query ="""INSERT INTO requests (ReqID, request_date, item, model_number, quantity, vendor, unit_price, ship_price, receive_date, requestor) 
			VALUES (%s,'%s','%s','%s',%s,'%s',%s,%s,NULL,'%s')""" % (ReqID, req_date, item, model_number, quantity, vendor, unit_price, ship_price, requestor)
	# The connection object.
	c = connection.cursor()
	# Execute query by connection object
	c.execute(query)
	
	return requests(request)

def recItem(request):
	##Retreive Input
	ReqID = request.GET.get('ReqID')
	currdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

	query ="""UPDATE requests
			SET receive_date = '%s'
			WHERE ReqID = %s 
			AND ReqID IN(
				SELECT a.ReqID FROM approval a
			)""" % (currdate, ReqID)
	c = connection.cursor()
	c.execute(query)

	#Print Updated
	
	return requests(request)

def delReq(request):
	##Retreive Input
	ReqID = request.GET.get('ReqID')

	query ="""DELETE FROM approval WHERE ReqID = %s;
			DELETE FROM requests WHERE ReqID = %s; """ % (ReqID, ReqID)
	c = connection.cursor()
	c.execute(query)

	#Print Updated
	
	return requests(request)

def pendApr(request):
	## Query
	query ="""SELECT ReqID,m.first_name ||' '||m.last_name AS name, request_date, item, model_number, quantity, vendor, unit_price, ship_price, (CASE 
																									 WHEN receive_date IS NULL
																									 AND ReqID NOT IN (
																									 SELECT ReqID FROM approval)
																									 THEN CAST('Pending Approval'AS VARCHAR(64))
																									 WHEN receive_date IS NULL THEN CAST('Pending Delivery' AS VARCHAR(64))
																									 ELSE CAST('Received: ' || receive_date AS VARCHAR(64))
																									 END) AS status 
			FROM requests r, members m
			WHERE r.requestor = m.email
			AND r.ReqID NOT IN(
				SELECT a.ReqID FROM approval a) 
			ORDER BY request_date DESC"""
	# The connection object.
	c = connection.cursor()
	# Execute query by connection object
	c.execute(query)
	# Fetch all the rows. fetchall() returns a list of tuples.
	requests = c.fetchall()
	requests_dict = {'requests': requests}
	return render(request,'AppPR/requests.html',requests_dict)

def pendDel(request):
	## Query
	query ="""SELECT ReqID,m.first_name ||' '||m.last_name AS name, request_date, item, model_number, quantity, vendor, unit_price, ship_price, (CASE 
																									 WHEN receive_date IS NULL
																									 AND ReqID NOT IN (
																									 SELECT ReqID FROM approval)
																									 THEN CAST('Pending Approval'AS VARCHAR(64))
																									 WHEN receive_date IS NULL THEN CAST('Pending Delivery' AS VARCHAR(64))
																									 ELSE CAST('Received: ' || receive_date AS VARCHAR(64))
																									 END) AS status 
			FROM requests r, members m
			WHERE r.ReqID IN(
				SELECT a.ReqID FROM approval a)
			AND r.receive_date IS NULL AND r.requestor = m.email
			ORDER BY request_date DESC"""
	# The connection object.
	c = connection.cursor()
	# Execute query by connection object
	c.execute(query)
	# Fetch all the rows. fetchall() returns a list of tuples.
	requests = c.fetchall()
	requests_dict = {'requests': requests}
	return render(request,'AppPR/requests.html',requests_dict)

def aprReq(request):
	##Retreive Input
	ReqID = request.GET.get('ReqID')
	currdate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	staff_approver = request.GET.get('staff_approver')
	staff_password = request.GET.get('staff_password')


	query ="""INSERT INTO approval(staff_approver, approve_date, ReqID)
			SELECT m.email,'%s', r.ReqID
			FROM members m, requests r
			WHERE m.role = 'Staff' AND m.email = '%s' AND r.ReqID = %s AND r.requestor <> m.email AND m.password = '%s';""" % (currdate, staff_approver, ReqID, staff_password)
	c = connection.cursor()
	c.execute(query)
	
	#Print Updated
	return requests(request)

def addMember(request):
	##Retreive Input
	first_name = request.GET.get('first_name')
	last_name = request.GET.get('last_name')
	email = request.GET.get('email')
	role = request.GET.get('role')
	password = request.GET.get('password')

	query ="""INSERT INTO members(first_name, last_name, email, role, password)
			VALUES('%s','%s','%s','%s','%s')""" % (first_name, last_name, email, role, password)
	c = connection.cursor()
	c.execute(query)
	
	#Print Updated
	return members(request)
	
