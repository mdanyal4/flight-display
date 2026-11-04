// clear old flight details when data is missing or outdated
function clearFlight(message) {
    document.getElementById("status").textContent = message;

    const fields = [
        "airline", "callsign", "departure", "arrival",
        "aircraft", "altitude", "distance"
    ];

    for (const field of fields) {
        document.getElementById(field).textContent = "—";
    }
}

// read the latest file saved by python
async function updateFlight() {
    try {
        const response = await fetch("flight.json", { cache: "no-store" });

        if (!response.ok) {
            throw new Error("Could not load flight.json");
        }

        const flight = await response.json();

        // python timestamp is in seconds, javascript uses milliseconds
        const age = Date.now() / 1000 - flight.updated_at;

        // stop showing old details if python hasn't updated recently
        if (!Number.isFinite(age) || age > 90) {
            clearFlight("Waiting for update");
            return;
        }

        if (!flight.available) {
            clearFlight("No nearby flight found");
            return;
        }

        // replace the page's text with the latest flight details
        document.getElementById("status").textContent =
            "Nearby Flight";

        document.getElementById("airline").textContent = flight.airline;
        document.getElementById("callsign").textContent = flight.callsign;
        document.getElementById("departure").textContent = flight.departure;
        document.getElementById("arrival").textContent = flight.arrival;
        document.getElementById("aircraft").textContent = flight.aircraft;

        // format altitude with commas and distance with two decimal places
        document.getElementById("altitude").textContent =
            flight.altitude.toLocaleString("en-US");
        document.getElementById("distance").textContent =
            flight.distance.toFixed(2);
    } catch (error) {
        clearFlight("Waiting for flight data");
        console.error(error);
    } finally {
        // check the local file again in 5 seconds
        setTimeout(updateFlight, 5000);
    }
}

// clear sample values and start checking
clearFlight("Loading flight data...");
updateFlight();