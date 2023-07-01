from flask import Blueprint, render_template, request
import copy
from logic.cspSetup import EventBulletin, ProvidedProfile, ItinCSPConstructor, HotelCSPConstructor
from logic.cspSolver import BacktrackingSearch

bulletin = EventBulletin('logic/Telluride.json')
hotels = EventBulletin('logic/hotels.json')
restaurants = EventBulletin('logic/eat.json')

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    print('test')
    if request.method == 'POST':
        data = request.form
        profile = ProvidedProfile(int(data['days']), [data['pref1'], data['pref2'], data['pref3']], int(data['cost']))

        cspConstructor = ItinCSPConstructor(bulletin, copy.deepcopy(profile))
        cspHotel = HotelCSPConstructor(hotels, copy.deepcopy(profile))
        cspEat = HotelCSPConstructor(restaurants, copy.deepcopy(profile))

        csp = cspConstructor.get_basic_csp()
        hotel = cspHotel.get_basic_csp()
        eat = cspEat.get_basic_csp()

        cspConstructor.add_all_additional_constraints(csp)
        cspHotel.add_constraints(hotel)
        cspEat.add_constraints(eat)

        alg = BacktrackingSearch()
        res = alg.solve(csp, False, False)

        hAlg = BacktrackingSearch()
        hres = hAlg.solve(hotel, False, False)

        eAlg = BacktrackingSearch()
        rres = eAlg.solve(eat, False, False)

        if profile.days > 1:
            return render_template("result.html", result = res, bulletin = bulletin, days = profile.days, hotel = hres, restaurant = rres, hbulletin = hotels, rbulletin = restaurants)
        else:
            return render_template("result.html", result = res, bulletin = bulletin, days = profile.days, restaurant = rres, rbulletin = restaurants)

    return render_template("home.html")