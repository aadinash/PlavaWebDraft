import copy
from cspSetup import EventBulletin, EventProfile, ItinCSPConstructor, HotelCSPConstructor
from cspSolver import BacktrackingSearch

bulletin = EventBulletin('python/Telluride.json')
profile = EventProfile('python/itin1.txt')

hotels = EventBulletin('python/hotels.json')
restaurants = EventBulletin('python/eat.json')

# Initialize a CSPConstructor object for events using both the event bulletin and profile
cspConstructor = ItinCSPConstructor(bulletin, copy.deepcopy(profile))

# Initialize a HotelChoice object that contains factors to solve for the chosen hotel using the hotel bulletin and profile
cspHotel = HotelCSPConstructor(hotels, copy.deepcopy(profile))
cspEat = HotelCSPConstructor(restaurants, copy.deepcopy(profile))

# Create the actual CSP from the CSPConstructor objects method
csp = cspConstructor.get_basic_csp()
hotel = cspHotel.get_basic_csp()
eat = cspEat.get_basic_csp()

# add on constraints to the CSP we created using the more CSPConstructor methods
cspConstructor.add_all_additional_constraints(csp)
cspHotel.add_constraints(hotel)
cspEat.add_constraints(eat)

# call the solver on the CSP with all the added constraints
alg = BacktrackingSearch()
print(alg.solve(csp, False, False))

hAlg = BacktrackingSearch()
print(hAlg.solve(hotel, False, False))

eAlg = BacktrackingSearch()
dict = eAlg.solve(eat, False, False)
dict["restaurant"] = dict.pop("choice")
print(dict)