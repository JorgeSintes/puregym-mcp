from datetime import date

from puregym_mcp.puregym.client import parse_dashboard_bookings, parse_dashboard_datetime


def test_parse_dashboard_bookings_extracts_bookings_and_waitlist():
    html = """
    <div class="card-wrap">
      <div class="card-wrap__card" id="card-1">
        <div class="card-wrap__card-title"><h2>2026-03-23 09:00</h2></div>
        <div class="card-wrap__card-text">
          <p>
            <b>Bike Standard</b><br>
            Kbh Ø., Århusgade<br>
            <br>
            <b></b>
          </p>
          <a class="cancelClassLink" data-pid="pid-1">Frameld</a>
        </div>
      </div>
      <div class="card-wrap__card" id="card-2">
        <div class="card-wrap__card-title"><h2>2026-04-07 17:00</h2></div>
        <div class="card-wrap__card-text">
          <p>
            <b>Bike Standard</b><br>
            Kbh Ø., Strandvejen<br>
            <br>
            <b>Du er nr. 11 på ventelisten</b>
          </p>
          <a class="cancelClassLink" data-pid="pid-2">Frameld</a>
        </div>
      </div>
    </div>
    """

    bookings = parse_dashboard_bookings(html)

    assert len(bookings) == 2
    assert bookings[0].date == "2026-03-23"
    assert bookings[0].startTime == "09:00:00"
    assert bookings[0].title == "Bike Standard"
    assert bookings[0].location == "Kbh Ø., Århusgade"
    assert bookings[0].participationId == "pid-1"
    assert bookings[0].is_waitlisted is False
    assert bookings[1].button_description == "Du er nr. 11 på ventelisten"
    assert bookings[1].waitlist_position == 11


def test_parse_dashboard_datetime_handles_relative_labels():
    today = date(2026, 3, 21)

    assert parse_dashboard_datetime("I dag  08:00", today) == parse_dashboard_datetime(
        "2026-03-21 08:00", today
    )
    assert parse_dashboard_datetime("I morgen 17:40", today) == parse_dashboard_datetime(
        "2026-03-22 17:40", today
    )
