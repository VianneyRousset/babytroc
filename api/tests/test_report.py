import json

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.enums import ReportType
from app.models.report import Report
from app.schemas.item.read import ItemRead
from app.schemas.loan.read import LoanRequestRead
from app.schemas.user.private import UserPrivateRead


class TestReportUser:
    """Test user report endpoint."""

    async def test_report_user(
        self,
        alice_client: AsyncClient,
        bob: UserPrivateRead,
        database_sessionmaker: async_sessionmaker,
    ):
        """Report a user, verify DB row and snapshot content."""
        resp = await alice_client.post(
            f"/api/v1/users/{bob.id}/report",
            json={"message": "Inappropriate behavior", "context": "In chat"},
        )
        assert resp.status_code == status.HTTP_201_CREATED

        async with database_sessionmaker.begin() as session:
            reports = (
                await session.execute(
                    select(Report).where(Report.report_type == ReportType.user)
                )
            ).scalars().all()
            assert len(reports) >= 1
            report = reports[-1]
            assert report.description == "Inappropriate behavior"
            assert report.context == "In chat"
            info = json.loads(report.saved_info)
            assert info["name"] == bob.name
            assert info["email"] == bob.email

    async def test_report_user_snapshot_preserved(
        self,
        alice_client: AsyncClient,
        bob: UserPrivateRead,
        bob_client: AsyncClient,
        database_sessionmaker: async_sessionmaker,
    ):
        """Snapshot preserves original name even after user changes it."""
        original_name = bob.name

        resp = await alice_client.post(
            f"/api/v1/users/{bob.id}/report",
            json={"message": "Bad content", "context": "Profile"},
        )
        assert resp.status_code == status.HTTP_201_CREATED

        # bob changes name
        resp = await bob_client.post(
            "/api/v1/me",
            json={"name": "newbobname"},
        )
        resp.raise_for_status()

        # verify snapshot still has original name
        async with database_sessionmaker.begin() as session:
            reports = (
                await session.execute(
                    select(Report).where(Report.report_type == ReportType.user)
                )
            ).scalars().all()
            report = reports[-1]
            info = json.loads(report.saved_info)
            assert info["name"] == original_name

    async def test_report_non_existent_user(
        self,
        alice_client: AsyncClient,
    ):
        resp = await alice_client.post(
            "/api/v1/users/999999/report",
            json={"message": "test", "context": "test"},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_report_user_no_auth(
        self,
        client: AsyncClient,
        bob: UserPrivateRead,
    ):
        resp = await client.post(
            f"/api/v1/users/{bob.id}/report",
            json={"message": "test", "context": "test"},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.usefixtures("items")
class TestReportItem:
    """Test item report endpoint."""

    async def test_report_item(
        self,
        alice_client: AsyncClient,
        bob_items: list[ItemRead],
        database_sessionmaker: async_sessionmaker,
    ):
        """Report an item, verify snapshot contains item details."""
        item = bob_items[0]

        resp = await alice_client.post(
            f"/api/v1/items/{item.id}/report",
            json={"message": "Policy violation", "context": "Item listing"},
        )
        assert resp.status_code == status.HTTP_201_CREATED

        async with database_sessionmaker.begin() as session:
            reports = (
                await session.execute(
                    select(Report).where(Report.report_type == ReportType.item)
                )
            ).scalars().all()
            assert len(reports) >= 1
            report = reports[-1]
            info = json.loads(report.saved_info)
            assert info["id"] == item.id
            assert info["name"] == item.name
            assert info["description"] == item.description
            assert "owner" in info
            assert info["owner"]["id"] == item.owner.id

    async def test_report_non_existent_item(
        self,
        alice_client: AsyncClient,
    ):
        resp = await alice_client.post(
            "/api/v1/items/999999/report",
            json={"message": "test", "context": "test"},
        )
        assert resp.status_code == status.HTTP_404_NOT_FOUND

    async def test_report_item_no_auth(
        self,
        client: AsyncClient,
        bob_items: list[ItemRead],
    ):
        resp = await client.post(
            f"/api/v1/items/{bob_items[0].id}/report",
            json={"message": "test", "context": "test"},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED


class TestReportChat:
    """Test chat report endpoint."""

    async def test_report_chat(
        self,
        alice_client: AsyncClient,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
        database_sessionmaker: async_sessionmaker,
    ):
        """Report a chat, verify snapshot contains messages and members."""
        chat_id = bob_new_loan_request_for_alice_new_item.chat_id

        resp = await alice_client.post(
            f"/api/v1/me/chats/{chat_id}/report",
            json={"message": "Harassment", "context": "Chat conversation"},
        )
        assert resp.status_code == status.HTTP_201_CREATED

        async with database_sessionmaker.begin() as session:
            reports = (
                await session.execute(
                    select(Report).where(Report.report_type == ReportType.chat)
                )
            ).scalars().all()
            assert len(reports) >= 1
            report = reports[-1]
            info = json.loads(report.saved_info)
            assert "messages" in info
            assert len(info["messages"]) >= 1
            assert "owner" in info
            assert "borrower" in info
            assert "item" in info

    async def test_report_chat_not_member(
        self,
        carol_client: AsyncClient,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        """Non-member cannot report a chat."""
        chat_id = bob_new_loan_request_for_alice_new_item.chat_id
        resp = await carol_client.post(
            f"/api/v1/me/chats/{chat_id}/report",
            json={"message": "test", "context": "test"},
        )
        assert resp.is_error

    async def test_report_non_existent_chat(
        self,
        alice_client: AsyncClient,
    ):
        resp = await alice_client.post(
            "/api/v1/me/chats/999999-999999/report",
            json={"message": "test", "context": "test"},
        )
        assert resp.is_error

    async def test_report_chat_no_auth(
        self,
        client: AsyncClient,
        bob_new_loan_request_for_alice_new_item: LoanRequestRead,
    ):
        chat_id = bob_new_loan_request_for_alice_new_item.chat_id
        resp = await client.post(
            f"/api/v1/me/chats/{chat_id}/report",
            json={"message": "test", "context": "test"},
        )
        assert resp.status_code == status.HTTP_401_UNAUTHORIZED
