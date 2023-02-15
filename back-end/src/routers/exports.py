from typing import Dict, List, Optional, Tuple
from colorama import Fore
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from miniopy_async import Minio

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from fastapi.responses import JSONResponse

from ..models.exports import ExportsPage, ExportLogPackage

from ..internal.auth import check_is_admin
from ..internal.dependencies.mongo_client import get_db
from ..internal.dependencies.minio_client import (
    minio_api_client,
    remove_data_from_prefix,
)

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
                lookup["timeInitiated"] = {
                    "$gte": pages_export.time_initiated_range["from"],
                    "$lte": pages_export.time_initiated_range["to"],
                }
        # narrow search by looking for time completed within a time range given by req
        if pages_export.time_completed_range is not None:
            if isinstance(pages_export.time_completed_range, dict):
                lookup["timeCompleted"] = {
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
async def remove_exports(
    log_package: ExportLogPackage,
    s3_client: Minio = Depends(minio_api_client),
    db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient] = Depends(get_db),
):
    db, mongo_client = db
    exports_list = log_package.logs_package
    failed_exports_removals = []
    async with await mongo_client.start_session() as session:
        async with session.start_transaction():
            check = await (
                db["exports"]
                .find({"$or": list(map(lambda x: x.dict(by_alias=True), exports_list))})
                .to_list(len(exports_list))
            )

            for x in check:
                (model_bucket, prefix) = (
                    x["exportLocation"].split("s3://")[1].split("/", 1)
                )
                errors = await remove_data_from_prefix(s3_client, prefix, model_bucket)
                for error in errors:
                    if error is not None:
                        failed_exports_removals.append(x["exportLocation"])
                        print(
                            f"{Fore.YELLOW}WARNING{Fore.WHITE}:  Removal of export '{prefix}' from S3 bucket failed! Skipping..."
                        )
                        continue
                await db["exports"].delete_one(
                    {
                        "userId": x["userId"],
                        "timeInitiated": x["timeInitiated"],
                        "timeCompleted": x["timeCompleted"],
                    }
                )
            if len(failed_exports_removals) > 0:
                return JSONResponse(
                    status_code=status.HTTP_206_PARTIAL_CONTENT,
                    content=f"Exports of {str(failed_exports_removals)} failed",
                )
