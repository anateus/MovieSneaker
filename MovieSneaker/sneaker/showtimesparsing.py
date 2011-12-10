import lxml.html as html
import datetime
import re

# TODO: Refactor this shitshow. Just use a much more straightforward interface:
# Basically, I need to define an intermediate data model, perhaps json
# and the ShowtimeParser abstract class will do validation, otherwise
# each class can just do its own custom shit

class ShowtimeParser:
	base = None
	zipcode = None
	date = None
		
# TODO: fake the useragent


class FlixsterParser(ShowtimeParser):
	# The date is in the format: YYYYMMDD, zipcode is: NNNNN
	BASE_URL = "http://igoogle.flixster.com/igoogle/showtimes?movie=all&date=%(date)s&postal=%(zipcode)s&submit=Go"
	#USERAGENT = "Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405"
	
	def __init__(self,zipcode=None,date=None):
		"""
		:param date: Datetime object representing our target date
		:param zipcode: The zipcode as a string

		:return:
		"""
		if zipcode:
			if not date:
				date = datetime.datetime.today()
			self.zipcode = zipcode
			self.date = date
			self._get_base(date=date.strftime("%Y%m%d"),zipcode=zipcode)
			self._parse()
			
	
	def _get_base(self,**kwargs):
		self.base = html.parse(self.BASE_URL%kwargs).getroot()

	def _parse(self):
		theatres = []
		for theater in self.base.find_class('theater'):
			name = theater.cssselect('h2 a')[0].attrib['title']
			address = theater.cssselect('h2 span')[0].text.strip("\n\t -")
			movies = []
			for movie in theater.cssselect('.showtime'):
				title_line = movie.cssselect('h3')[0]
				if len(title_line.getchildren())>1:
					title = title_line.cssselect('a')[0].attrib['title']
					sp = title_line.cssselect('span')[0].text.strip("\n\t -").rsplit('-',1)
					raw_rating = sp[0]
					if len(sp)>1:
						raw_duration = sp[1]
						split_duration = raw_duration.strip().split()
						parsed_duration = 0
						while split_duration:
							num = split_duration.pop(0)
							kind = split_duration.pop(0)
							parsed_duration += 60*int(num)if 'hr' in kind.lower() else int(num)
						duration = datetime.timedelta(minutes=parsed_duration)
					else:
						# if no duration specified we'll assume 3 hours
						# probably double feature
						duration = datetime.timedelta(minutes=180)
				else: # we have nothing but a non-linked title
					title = title_line.text.strip()
					duration = datetime.timedelta(minutes=90)
				showtimes = []
				for raw_time in movie.cssselect('h3')[0].tail.split():
					if not raw_time.endswith("am"):
						raw_time += "pm"
					# combine the hour with the date of this parse
					start = datetime.datetime.combine(self.date,datetime.datetime.strptime(raw_time,"%I:%M%p").time())
					end = start + duration
					showtimes.append({"start":start,"end":end})
				movies.append({'name':title,'showtimes':showtimes})
			theatres.append({'name':name,'address':address,'movies':movies})
		self.theatres = theatres
		return theatres

if __name__=="__main__":
	fp = FlixsterParser("94043")
	