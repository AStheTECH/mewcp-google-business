"""Accounts group: list_accounts, get_account, create_account, update_account,
list_account_admins, list_invitations, list_location_admins."""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..logging_utils import ToolLogger
from ..schemas.accounts import (
    AccountAdminListData,
    AccountAdminListResult,
    AccountCreateData,
    AccountCreateResult,
    AccountData,
    AccountGetData,
    AccountGetResult,
    AccountListData,
    AccountListResult,
    AccountUpdateData,
    AccountUpdateResult,
    InvitationListData,
    InvitationListResult,
    LocationAdminListData,
    LocationAdminListResult,
)
from ._helpers import _err, _handle_request_exc

logger = logging.getLogger("google-business-mcp.tools.accounts")


def register_accounts_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="list_accounts",
        description=(
            "Lists the accounts the authenticated user owns or has management rights to (or, "
            "with parent_account, the accounts directly accessible from an Organization or User "
            "Group), and returns the Account objects with a next-page token. The user's personal "
            "account is always the first item unless filtered out, and `type` is the only "
            "supported filter field."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def list_accounts(
        parent_account: str | None = Field(
            default=None,
            description="Resource name of the account whose directly accessible accounts to "
            "list, in the form accounts/{account_id}. Only meaningful for Organizations and "
            "User Groups. Omit to list accounts for the authenticated user.",
        ),
        page_size: int | None = Field(
            default=None,
            description="How many accounts to fetch per page, 1 to 20. Omit to use the default of 20.",
        ),
        page_token: str | None = Field(
            default=None,
            description="Token from a previous call's nextPageToken to fetch the next page. "
            "Omit for the first page.",
        ),
        filter_: str | None = Field(
            default=None,
            description="Filter on account type, e.g. type=USER_GROUP returns only user groups. "
            "`type` is the only supported filter. Omit to return all accounts (paginated).",
        ),
    ) -> AccountListResult:
        tlog = ToolLogger(logger, "list_accounts")

        if page_size is not None and not (1 <= page_size <= 20):
            return _err(AccountListResult, tlog, "VALIDATION_ERROR",
                "page_size must be between 1 and 20", 400)

        try:
            svc = service.get_account_management_service()
            resp = svc.accounts().list(
                parentAccount=parent_account, pageSize=page_size,
                pageToken=page_token, filter=filter_,
            ).execute()
            tlog.success()
            return AccountListResult(success=True, statusCode=200, data=AccountListData(**resp))
        except Exception as exc:
            return _handle_request_exc(AccountListResult, tlog, exc)

    @mcp.tool(
        name="get_account",
        description=(
            "Returns the specified account, including its name, type, role, permission level, "
            "verification and vetted state, and organization info for organization accounts. "
            "If the account does not exist or the caller has no access rights to it, the call "
            "fails with statusCode 404 and error code UPSTREAM_ERROR."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def get_account(
        name: str = Field(
            description="Resource name of the account to fetch, in the form accounts/{account_id}."
        ),
    ) -> AccountGetResult:
        tlog = ToolLogger(logger, "get_account")
        try:
            svc = service.get_account_management_service()
            resp = svc.accounts().get(name=name).execute()
            tlog.success()
            return AccountGetResult(success=True, statusCode=200, data=AccountGetData(**resp))
        except Exception as exc:
            return _handle_request_exc(AccountGetResult, tlog, exc)

    @mcp.tool(
        name="create_account",
        description=(
            "Creates an account of the given type and primary owner, and returns the new Account. "
            "Personal accounts and Organizations cannot be created; User Groups cannot have a "
            "Personal account as primary owner; Location Groups cannot have as primary owner a "
            "Personal account that belongs to an Organization, and cannot be owned by another "
            "Location Group."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def create_account(
        account_name: str = Field(description="The name of the account to create."),
        primary_owner: str = Field(
            description="Resource name of the account that will be the primary owner of the "
            "new account, in the form accounts/{account_id}."
        ),
        type: str = Field(
            description="Account type: LOCATION_GROUP (a group of Locations) or USER_GROUP "
            "(a User Group for segregating organization staff). PERSONAL and ORGANIZATION "
            "cannot be created using this API."
        ),
    ) -> AccountCreateResult:
        tlog = ToolLogger(logger, "create_account")
        try:
            svc = service.get_account_management_service()
            resp = svc.accounts().create(
                body={"accountName": account_name, "primaryOwner": primary_owner, "type": type},
            ).execute()
            tlog.success()
            return AccountCreateResult(success=True, statusCode=200, data=AccountCreateData(**resp))
        except Exception as exc:
            return _handle_request_exc(AccountCreateResult, tlog, exc)

    @mcp.tool(
        name="update_account",
        description=(
            "Updates the specified business account's accountName (the only editable field) and "
            "returns the updated Account; Personal accounts cannot be updated. Only the fields "
            "you provide are changed — others keep their current value. NOTE: this overwrites "
            "the current field values — the original state is not stored after the call. The "
            "response includes both the before and after state so you have a full record of "
            "what changed."
        ),
        annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, openWorldHint=True),
    )
    def update_account(
        name: str = Field(
            description="Resource name of the account to update, in the form accounts/{account_id}."
        ),
        update_mask: str = Field(
            description="The fields to update. The only editable field is accountName."
        ),
        account_name: str = Field(description="The new name of the account."),
        validate_only: bool | None = Field(
            default=None,
            description="If true, validates the request without actually updating the account. "
            "Omit to apply the update.",
        ),
    ) -> AccountUpdateResult:
        tlog = ToolLogger(logger, "update_account")
        try:
            svc = service.get_account_management_service()
            before = svc.accounts().get(name=name).execute()
            after = svc.accounts().patch(
                name=name, updateMask=update_mask, validateOnly=validate_only,
                body={"accountName": account_name},
            ).execute()
            tlog.success()
            return AccountUpdateResult(
                success=True, statusCode=200,
                data=AccountUpdateData(before=AccountData(**before), after=AccountData(**after)),
            )
        except Exception as exc:
            return _handle_request_exc(AccountUpdateResult, tlog, exc)

    @mcp.tool(
        name="list_account_admins",
        description=(
            "Lists the admins of the specified account and returns each admin's resource name, "
            "name (or invitee email while pending), role, and whether their invitation is still pending."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def list_account_admins(
        parent: str = Field(
            description="Resource name of the account whose admins to list, in the form "
            "accounts/{account_id} (without a trailing /admins)."
        ),
    ) -> AccountAdminListResult:
        tlog = ToolLogger(logger, "list_account_admins")
        try:
            svc = service.get_account_management_service()
            resp = svc.accounts().admins().list(parent=parent).execute()
            tlog.success()
            return AccountAdminListResult(
                success=True, statusCode=200, data=AccountAdminListData(**resp))
        except Exception as exc:
            return _handle_request_exc(AccountAdminListResult, tlog, exc)

    @mcp.tool(
        name="list_invitations",
        description=(
            "Lists the pending invitations for the specified account (at most 1000), optionally "
            "filtered by target type, and returns each invitation's resource name, invited role, "
            "target type, and target account or location."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def list_invitations(
        parent: str = Field(
            description="Resource name of the account whose invitations to list, in the form "
            "accounts/{account_id} (without a trailing /invitations)."
        ),
        filter_: str | None = Field(
            default=None,
            description="Filter on the invitation's target type (Invitation.target_type); "
            "filterable values are ACCOUNTS_ONLY and LOCATIONS_ONLY, e.g. "
            "target_type=ACCOUNTS_ONLY (snake_case field name; targetType is rejected). "
            "Omit to return all pending invitations.",
        ),
    ) -> InvitationListResult:
        tlog = ToolLogger(logger, "list_invitations")
        try:
            svc = service.get_account_management_service()
            resp = svc.accounts().invitations().list(parent=parent, filter=filter_).execute()
            tlog.success()
            return InvitationListResult(
                success=True, statusCode=200, data=InvitationListData(**resp))
        except Exception as exc:
            return _handle_request_exc(InvitationListResult, tlog, exc)

    @mcp.tool(
        name="list_location_admins",
        description=(
            "Lists all admins of the specified location and returns each admin's resource name, "
            "name (or invitee email while pending), role, and whether their invitation is still pending."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def list_location_admins(
        parent: str = Field(
            description="Resource name of the location whose admins to list, in the form "
            "locations/{location_id} (without a trailing /admins)."
        ),
    ) -> LocationAdminListResult:
        tlog = ToolLogger(logger, "list_location_admins")
        try:
            svc = service.get_account_management_service()
            resp = svc.locations().admins().list(parent=parent).execute()
            tlog.success()
            return LocationAdminListResult(
                success=True, statusCode=200, data=LocationAdminListData(**resp))
        except Exception as exc:
            return _handle_request_exc(LocationAdminListResult, tlog, exc)
