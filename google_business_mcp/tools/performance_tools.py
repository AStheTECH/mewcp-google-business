"""Performance group: get_daily_metrics_time_series, fetch_multi_daily_metrics_time_series,
list_search_keyword_impressions_monthly."""

import logging

from fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .. import service
from ..logging_utils import ToolLogger
from ..schemas.performance import (
    DailyMetricsTimeSeriesData,
    DailyMetricsTimeSeriesResult,
    MultiDailyMetricsTimeSeriesData,
    MultiDailyMetricsTimeSeriesResult,
    SearchKeywordImpressionsMonthlyData,
    SearchKeywordImpressionsMonthlyResult,
)
from ._helpers import _err, _handle_request_exc

logger = logging.getLogger("google-business-mcp.tools.performance")


def _flatten_date(prefix: str, date: dict) -> dict:
    """Flatten a {year, month, day} dict into googleapiclient query kwargs, skipping absent keys."""
    kwargs = {}
    for key in ("year", "month", "day"):
        value = date.get(key)
        if value is not None:
            kwargs[f"{prefix}_{key}"] = value
    return kwargs


def _flatten_daily_range(daily_range: dict) -> dict:
    kwargs = {}
    kwargs.update(_flatten_date("dailyRange_startDate", daily_range["startDate"]))
    kwargs.update(_flatten_date("dailyRange_endDate", daily_range["endDate"]))
    return kwargs


def _flatten_monthly_range(monthly_range: dict) -> dict:
    kwargs = {}
    kwargs.update(_flatten_date("monthlyRange_startMonth", monthly_range["startMonth"]))
    kwargs.update(_flatten_date("monthlyRange_endMonth", monthly_range["endMonth"]))
    return kwargs


def _flatten_daily_sub_entity_type(daily_sub_entity_type: dict) -> dict:
    kwargs = {}
    day_of_week = daily_sub_entity_type.get("dayOfWeek")
    if day_of_week is not None:
        kwargs["dailySubEntityType_dayOfWeek"] = day_of_week
    time_of_day = daily_sub_entity_type.get("timeOfDay")
    if time_of_day is not None:
        for key in ("hours", "minutes", "seconds", "nanos"):
            value = time_of_day.get(key)
            if value is not None:
                kwargs[f"dailySubEntityType_timeOfDay_{key}"] = value
    return kwargs


def register_performance_tools(mcp: FastMCP) -> None:

    @mcp.tool(
        name="get_daily_metrics_time_series",
        description=(
            "Returns the values for each date in a given time range for a single specified daily metric. "
            "Only daily data is available; hourly metrics are not supported."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def get_daily_metrics_time_series(
        name: str = Field(
            description=(
                "The location for which the time series should be fetched. "
                "Format: `locations/{locationId}` where `locationId` is an unobfuscated listing id."
            )
        ),
        daily_metric: str = Field(
            description=(
                "The metric to retrieve time series for. One of: "
                "`BUSINESS_IMPRESSIONS_DESKTOP_MAPS`, `BUSINESS_IMPRESSIONS_DESKTOP_SEARCH`, "
                "`BUSINESS_IMPRESSIONS_MOBILE_MAPS`, `BUSINESS_IMPRESSIONS_MOBILE_SEARCH`, "
                "`BUSINESS_DIRECTION_REQUESTS`, `CALL_CLICKS`, `WEBSITE_CLICKS`, "
                "`MESSAGING_CLICKS` (clicks on the messaging button, e.g. WhatsApp), "
                "`BUSINESS_BOOKINGS`, `BUSINESS_FOOD_MENU_CLICKS`. "
                "Deprecated upstream: `BUSINESS_CONVERSATIONS`, `BUSINESS_FOOD_ORDERS`. "
                "`DAILY_METRIC_UNKNOWN` is the default unknown value."
            )
        ),
        daily_range: dict = Field(
            description=(
                "The timerange to fetch. "
                '`{ "startDate": {"year", "month", "day"}, "endDate": {"year", "month", "day"} }`, '
                "both inclusive."
            )
        ),
        daily_sub_entity_type: dict | None = Field(
            default=None,
            description=(
                "The sub-entity type/id the time series relates to. Currently no `DailyMetric` supports this "
                "(breakdown not available). Union of `dayOfWeek` (enum) or `timeOfDay` "
                '(`{"hours", "minutes", "seconds", "nanos"}`).'
            ),
        ),
    ) -> DailyMetricsTimeSeriesResult:
        tlog = ToolLogger(logger, "get_daily_metrics_time_series")

        if "startDate" not in daily_range or "endDate" not in daily_range:
            return _err(
                DailyMetricsTimeSeriesResult, tlog, "VALIDATION_ERROR",
                "daily_range must include 'startDate' and 'endDate'", 400,
            )

        try:
            kwargs = _flatten_daily_range(daily_range)
            if daily_sub_entity_type is not None:
                kwargs.update(_flatten_daily_sub_entity_type(daily_sub_entity_type))
            svc = service.get_performance_service()
            resp = svc.locations().getDailyMetricsTimeSeries(
                name=name, dailyMetric=daily_metric, **kwargs,
            ).execute()
            tlog.success()
            return DailyMetricsTimeSeriesResult(success=True, statusCode=200, data=DailyMetricsTimeSeriesData(**resp))
        except Exception as exc:
            return _handle_request_exc(DailyMetricsTimeSeriesResult, tlog, exc)

    @mcp.tool(
        name="fetch_multi_daily_metrics_time_series",
        description=(
            "Returns the values for each date in a given time range for multiple specified daily metrics at once. "
            "Only daily data is available; hourly metrics are not supported."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def fetch_multi_daily_metrics_time_series(
        location: str = Field(
            description=(
                "The location for which the time series should be fetched. "
                "Format: `locations/{locationId}` where `locationId` is an unobfuscated listing id."
            )
        ),
        daily_metrics: list[str] = Field(
            description=(
                "The metrics to retrieve time series for. Each one of: "
                "`BUSINESS_IMPRESSIONS_DESKTOP_MAPS`, `BUSINESS_IMPRESSIONS_DESKTOP_SEARCH`, "
                "`BUSINESS_IMPRESSIONS_MOBILE_MAPS`, `BUSINESS_IMPRESSIONS_MOBILE_SEARCH`, "
                "`BUSINESS_DIRECTION_REQUESTS`, `CALL_CLICKS`, `WEBSITE_CLICKS`, "
                "`MESSAGING_CLICKS` (clicks on the messaging button, e.g. WhatsApp), "
                "`BUSINESS_BOOKINGS`, `BUSINESS_FOOD_MENU_CLICKS`. "
                "Deprecated upstream: `BUSINESS_CONVERSATIONS`, `BUSINESS_FOOD_ORDERS`. "
                "`DAILY_METRIC_UNKNOWN` is the default unknown value."
            )
        ),
        daily_range: dict = Field(
            description=(
                "The timerange to fetch. "
                '`{ "startDate": {"year", "month", "day"}, "endDate": {"year", "month", "day"} }`, '
                "both inclusive."
            )
        ),
    ) -> MultiDailyMetricsTimeSeriesResult:
        tlog = ToolLogger(logger, "fetch_multi_daily_metrics_time_series")

        if "startDate" not in daily_range or "endDate" not in daily_range:
            return _err(
                MultiDailyMetricsTimeSeriesResult, tlog, "VALIDATION_ERROR",
                "daily_range must include 'startDate' and 'endDate'", 400,
            )

        try:
            kwargs = _flatten_daily_range(daily_range)
            svc = service.get_performance_service()
            resp = svc.locations().fetchMultiDailyMetricsTimeSeries(
                location=location, dailyMetrics=daily_metrics, **kwargs,
            ).execute()
            tlog.success()
            return MultiDailyMetricsTimeSeriesResult(
                success=True, statusCode=200, data=MultiDailyMetricsTimeSeriesData(**resp),
            )
        except Exception as exc:
            return _handle_request_exc(MultiDailyMetricsTimeSeriesResult, tlog, exc)

    @mcp.tool(
        name="list_search_keyword_impressions_monthly",
        description=(
            "Returns the search keywords used to find a business in Search or Maps, each accompanied by "
            "impression counts aggregated on a monthly basis."
        ),
        annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
    )
    def list_search_keyword_impressions_monthly(
        parent: str = Field(
            description=(
                "The location for which the time series should be fetched. "
                "Format: `locations/{locationId}` where `locationId` is an unobfuscated listing id."
            )
        ),
        monthly_range: dict = Field(
            description=(
                "The range in months to aggregate search keyword impressions over. "
                '`{ "startMonth": {"year", "month", "day"}, "endMonth": {"year", "month", "day"} }`, '
                "both inclusive — only year and month are considered."
            )
        ),
        page_size: int = Field(
            default=100,
            description="Number of results requested. Default 100, maximum 100.",
        ),
        page_token: str | None = Field(
            default=None,
            description="Base64-encoded token indicating the next paginated result to return.",
        ),
    ) -> SearchKeywordImpressionsMonthlyResult:
        tlog = ToolLogger(logger, "list_search_keyword_impressions_monthly")

        if "startMonth" not in monthly_range or "endMonth" not in monthly_range:
            return _err(
                SearchKeywordImpressionsMonthlyResult, tlog, "VALIDATION_ERROR",
                "monthly_range must include 'startMonth' and 'endMonth'", 400,
            )
        if page_size < 1 or page_size > 100:
            return _err(
                SearchKeywordImpressionsMonthlyResult, tlog, "VALIDATION_ERROR",
                "page_size must be between 1 and 100", 400,
            )

        try:
            kwargs = _flatten_monthly_range(monthly_range)
            svc = service.get_performance_service()
            resp = svc.locations().searchkeywords().impressions().monthly().list(
                parent=parent, pageSize=page_size, pageToken=page_token, **kwargs,
            ).execute()
            tlog.success()
            return SearchKeywordImpressionsMonthlyResult(
                success=True, statusCode=200, data=SearchKeywordImpressionsMonthlyData(**resp),
            )
        except Exception as exc:
            return _handle_request_exc(SearchKeywordImpressionsMonthlyResult, tlog, exc)
