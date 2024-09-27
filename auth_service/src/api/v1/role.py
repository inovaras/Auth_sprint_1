from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, Response

router = APIRouter()