from amadeus import Client, ResponseError

amadeus = Client(
    client_id='Oz15p7KCBhooPQN6XOKPbzLJ2Mj8jvst',
    client_secret='aYckjcokI2prSNkD'
)

try:
    response = amadeus.shopping.flight_offers_search.get(
        originLocationCode='HAN',
        destinationLocationCode='SGN',
        departureDate='2025-06-16',
        adults=1)
    print(response.data[0])
except ResponseError as error:
    print(error)