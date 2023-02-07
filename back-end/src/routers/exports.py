from typing import Dict, List, Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from minio import Minio

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from ..models.exports import ExportsPage, ExportLogPackage

from ..internal.auth import check_is_admin
from ..internal.dependencies.mongo_client import get_db
from ..internal.dependencies.minio_client import minio_api_client

router = APIRouter(prefix="/exports", tags=["Exports"])


@router.post(
    "/", status_code=status.HTTP_200_OK, dependencies=[Depends(check_is_admin)]
)
async def get_exported(
    pages_export: ExportsPage,
    descending: bool = Query(default=True, alias="desc"),
    sort_by: str = Query(default="timeInitiated", alias="sort"),
    db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db),
):
    db, mongo_client = db
    try:
        # check number of documents to skip past
        skips = pages_export.exports_num * (pages_export.page_num - 1)
        # dictionary for lookups
        lookup = {}
        # narrow search by exports that were initated by that userId
        if pages_export.userId is not None:
            lookup["userId"] = {"$regex": pages_export.userId, "$options": "i"}
        # narrow search by looking for time intiated within a time range given by req
        if pages_export.time_initiated_range is not None:
            if isinstance(pages_export.time_initiated_range, dict):
                lookup["created"] = {
                    "$gte": pages_export.time_initiated_range["from"],
                    "$lte": pages_export.time_initiated_range["to"],
                }
        # narrow search by looking for time completed within a time range given by req
        if pages_export.time_completed_range is not None:
            if isinstance(pages_export.time_completed_range, dict):
                lookup["time"] = {
                    "$gte": pages_export.time_completed_range["from"],
                    "$lte": pages_export.time_completed_range["to"],
                }
        async with await mongo_client.start_session() as session:
            async with session.start_transaction():
                total_rows = await (db["exports"].count_documents(lookup))
                if skips <= 0:
                    # find from users in MongodDB exclude ObjectID and convert to list
                    cursor = await (
                        db["exports"]
                        .find(lookup, {"_id": False})
                        .sort(sort_by, DESCENDING if descending else ASCENDING)
                        .limit(pages_export.exports_num)
                    ).to_list(length=pages_export.exports_num)
                # else call cursor with skips
                else:
                    # find from users in MongodDB exclude ObjectID and convert to list
                    cursor = await (
                        db["exports"]
                        .find(lookup, {"_id": False})
                        .sort(sort_by, DESCENDING if descending else ASCENDING)
                        .skip(skips)
                        .limit(pages_export.exports_num)
                    ).to_list(length=pages_export.exports_num)
        # return documents if all ok
        return {"results": cursor, "total_rows": total_rows}
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unable to get exports",
        ) from err
    # triggered if all else fails
    except Exception as err:
        # TODO: should the status code be 404?
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cannot find exports"
        ) from err


@router.delete(
    "/", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(check_is_admin)]
)
def remove_exports(
    log_package: ExportLogPackage,
    s3_client: Minio = Depends(minio_api_client),
    db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db),
):
    db, mongo_client = db
    log_package.logs_package