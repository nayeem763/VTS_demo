"""Admin API tests for durable, waypoint-based bus routes."""

from __future__ import annotations

import pytest
from django.urls import reverse

from apps.fleet.models import BusRoute, RouteStop

pytestmark = pytest.mark.django_db

LIST_URL = reverse("api:bus-route-list")


@pytest.fixture
def route_payload() -> dict:
    return {
        "name": "CU Shuttle",
        "start_longitude": "91.794230",
        "start_latitude": "22.470680",
        "stops": [
            {
                "name": "Science Faculty",
                "longitude": "91.791100",
                "latitude": "22.472400",
            },
            {
                "name": "Central Library",
                "longitude": "91.789300",
                "latitude": "22.473500",
            },
        ],
        "end_longitude": "91.787600",
        "end_latitude": "22.471600",
    }


def test_admin_can_create_list_and_delete_a_fixed_route(api_client, admin_user, route_payload):
    api_client.force_authenticate(user=admin_user)

    create_response = api_client.post(LIST_URL, route_payload, format="json")

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["name"] == "CU Shuttle"
    assert created["start_longitude"] == "91.794230"
    assert [(stop["sequence"], stop["name"]) for stop in created["stops"]] == [
        (1, "Science Faculty"),
        (2, "Central Library"),
    ]
    route = BusRoute.objects.get(pk=created["id"])
    assert list(route.stops.values_list("sequence", "name")) == [
        (1, "Science Faculty"),
        (2, "Central Library"),
    ]

    list_response = api_client.get(LIST_URL)

    assert list_response.status_code == 200
    assert list_response.json()["count"] == 1
    assert list_response.json()["results"][0]["id"] == route.id

    delete_response = api_client.delete(reverse("api:bus-route-detail", args=[route.id]))

    assert delete_response.status_code == 204
    assert not BusRoute.objects.filter(pk=route.id).exists()
    assert RouteStop.objects.count() == 0


def test_fixed_route_requires_an_admin(api_client, assigned_driver, route_payload):
    api_client.force_authenticate(user=assigned_driver)

    assert api_client.get(LIST_URL).status_code == 403
    assert api_client.post(LIST_URL, route_payload, format="json").status_code == 403


def test_fixed_route_rejects_duplicate_adjacent_waypoints(api_client, admin_user, route_payload):
    route_payload["stops"][0]["longitude"] = route_payload["start_longitude"]
    route_payload["stops"][0]["latitude"] = route_payload["start_latitude"]
    api_client.force_authenticate(user=admin_user)

    response = api_client.post(LIST_URL, route_payload, format="json")

    assert response.status_code == 400
    assert "different coordinates" in str(response.json())
    assert BusRoute.objects.count() == 0


def test_fixed_route_names_are_unique_ignoring_case(api_client, admin_user, route_payload):
    BusRoute.objects.create(
        name="CU Shuttle",
        start_longitude="91.700000",
        start_latitude="22.400000",
        end_longitude="91.710000",
        end_latitude="22.410000",
    )
    route_payload["name"] = "cu shuttle"
    api_client.force_authenticate(user=admin_user)

    response = api_client.post(LIST_URL, route_payload, format="json")

    assert response.status_code == 400
    assert "already exists" in str(response.json())
