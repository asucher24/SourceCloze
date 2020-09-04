
def get_user(request):
	if not request.user.is_authenticated:
		raise Exception("User not logged in.")
	return request.user.username
	# return request.user.username if request.user.username else request.user.email