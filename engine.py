
def load_high_score(text_file):
	file = open(text_file, 'r')
	high_score = file.read()
	return high_score

def save_high_score(text_file, score):
	file = open(text_file, 'w')
	file.write(str(score))