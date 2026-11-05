"""Schemas for the accounts tool group: list_accounts, get_account, create_account,
update_account, list_account_admins, list_invitations, list_location_admins."""

from pydantic import BaseModel, ConfigDict, Field

from ._base import ToolResult


class AccountData(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = Field(default=None, description="Resource name, accounts/{account_id}.")
    accountName: str | None = None
    accountNumber: str | None = None
    primaryOwner: str | None = None
    type: str | None = Field(
        default=None,
        description="ACCOUNT_TYPE_UNSPECIFIED, PERSONAL, LOCATION_GROUP, USER_GROUP, or ORGANIZATION.",
    )
    role: str | None = Field(
        default=None,
        description="ACCOUNT_ROLE_UNSPECIFIED, PRIMARY_OWNER, OWNER, MANAGER, or SITE_MANAGER.",
    )
    permissionLevel: str | None = Field(
        default=None,
        description="PERMISSION_LEVEL_UNSPECIFIED, OWNER_LEVEL, or MEMBER_LEVEL.",
    )
    verificationState: str | None = Field(
        default=None,
        description="VERIFICATION_STATE_UNSPECIFIED, VERIFIED, UNVERIFIED, or VERIFICATION_REQUESTED.",
    )
    vettedState: str | None = Field(
        default=None,
        description="VETTED_STATE_UNSPECIFIED, NOT_VETTED, VETTED, or INVALID.",
    )
    organizationInfo: dict | None = Field(
        default=None,
        description="Populated only for organization accounts: address, phoneNumber, registeredDomain.",
    )


class AccountListData(BaseModel):
    model_config = ConfigDict(extra="allow")

    accounts: list[AccountData] = Field(default_factory=list)
    nextPageToken: str | None = None


class AccountListResult(ToolResult):
    data: AccountListData | None = None


class AccountGetData(AccountData):
    """Fetched Account — same shape as AccountData."""


class AccountGetResult(ToolResult):
    data: AccountGetData | None = None


class AccountCreateData(AccountData):
    """Newly created Account — same shape as AccountData."""


class AccountCreateResult(ToolResult):
    data: AccountCreateData | None = None


class AccountUpdateData(BaseModel):
    model_config = ConfigDict(extra="allow")

    before: AccountData
    after: AccountData


class AccountUpdateResult(ToolResult):
    data: AccountUpdateData | None = None


class AdminData(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = Field(
        default=None,
        description="accounts/{account_id}/admins/{admin_id} or locations/{location_id}/admins/{admin_id}.",
    )
    admin: str | None = Field(
        default=None,
        description="Invitee email while the invitation is pending, otherwise the user's first and last names.",
    )
    account: str | None = None
    role: str | None = Field(
        default=None,
        description="ADMIN_ROLE_UNSPECIFIED, PRIMARY_OWNER, OWNER, MANAGER, or SITE_MANAGER.",
    )
    pendingInvitation: bool | None = None


class AccountAdminListData(BaseModel):
    model_config = ConfigDict(extra="allow")

    accountAdmins: list[AdminData] = Field(default_factory=list)


class AccountAdminListResult(ToolResult):
    data: AccountAdminListData | None = None


class LocationAdminListData(BaseModel):
    model_config = ConfigDict(extra="allow")

    admins: list[AdminData] = Field(default_factory=list)


class LocationAdminListResult(ToolResult):
    data: LocationAdminListData | None = None


class InvitationTargetLocationData(BaseModel):
    model_config = ConfigDict(extra="allow")

    locationName: str | None = None
    address: str | None = None
    placeId: str | None = None


class InvitationData(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str | None = Field(
        default=None, description="accounts/{account_id}/invitations/{invitation_id}."
    )
    role: str | None = Field(
        default=None,
        description="Invited role: ADMIN_ROLE_UNSPECIFIED, PRIMARY_OWNER, OWNER, MANAGER, or SITE_MANAGER.",
    )
    targetType: str | None = Field(
        default=None,
        description="TARGET_TYPE_UNSPECIFIED, ACCOUNTS_ONLY, or LOCATIONS_ONLY.",
    )
    targetAccount: AccountData | None = None
    targetLocation: InvitationTargetLocationData | None = None


class InvitationListData(BaseModel):
    model_config = ConfigDict(extra="allow")

    invitations: list[InvitationData] = Field(default_factory=list)


class InvitationListResult(ToolResult):
    data: InvitationListData | None = None
