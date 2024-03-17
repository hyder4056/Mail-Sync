import time
from typing import Any

from fastapi import Depends, Security
from fastapi_jwt import JwtAuthorizationCredentials

from src.authentication.service import access_security
from src.google.google_api_client import get_google_api_client
from src.google.models import EmailMetadata, GoogleOAuthCredentials
from src.link_mail_address.service import LinkMailAddressService
from src.openai.openai_client import OpenAIClient

from .models import (
    MailRequestBody,
    ProcessMailWithAIRequestBody,
    ProcessMailWithAIRequestType,
)
from dateutil.parser import parse


class MailSyncService:
    def __init__(
        self,
        link_mail_address_service: LinkMailAddressService = Depends(),
        openai_client: OpenAIClient = Depends(),
        jwt_credentials: JwtAuthorizationCredentials = Security(access_security),
    ):
        self.link_mail_address_service = link_mail_address_service
        self.openai_client = openai_client
        self.username = jwt_credentials.subject.get("username")

    async def get_mails(self, next_page_tokens_query=None) -> Any:
        start = time.time()
        # next_page_tokens_query = "email1,token1;email2,token2"
        next_page_tokens = (
            {x[0]: x[1] for x in [x.split(",") for x in next_page_tokens_query.split(";")]}
            if next_page_tokens_query
            else {}
        )
        print("next_page_tokens", next_page_tokens_query)
        oauth_tokens = await self.link_mail_address_service.get_all_oauth_tokens(self.username)
        google_api_clients = [
            get_google_api_client(
                GoogleOAuthCredentials(**token.oauth_tokens),
                token.email,
            )
            for token in oauth_tokens
        ]
        data = [client.get_user_mails(next_page_tokens.get(client.gmail, None)) for client in google_api_clients]

        end = time.time()
        print(f"Time taken: {end - start}")
        mails = [email for d in data for email in d.emails]
        mails.sort(key=lambda x: parse(x.date), reverse=True)  # Sort the mails list
        print("mails", mails)
        new_next_page_tokens = [
            {"next_page_token": d.next_page_token, "email": d.receiver} for d in data if d.next_page_token
        ]
        return {"mails": mails, "next_page_tokens": new_next_page_tokens}

    async def get_mail(self, mail_id: str, mail_address: str) -> Any:
        oauth_token = await self.link_mail_address_service.get_oauth_token_by_email(self.username, mail_address)
        google_api_client = get_google_api_client(oauth_token, mail_address)
        return google_api_client.get_user_mail(mail_id)

    async def send_mail(self, message: MailRequestBody) -> dict:
        oauth_token = await self.link_mail_address_service.get_oauth_token_by_email(self.username, message.sender)
        google_api_client = get_google_api_client(oauth_token, message.sender)
        return google_api_client.send_mail(message)
        # print(get_completion(f"You are a mail writer. Please help me write a reply to the mail: {message.message}"))
        # return {"message": "Mail sent successfully"}

    def _generate_prompt(self, request: ProcessMailWithAIRequestBody) -> dict:
        prompts = {
            ProcessMailWithAIRequestType.GENERATE: {
                "system_prompt": "You are an email generator.",
                "prompt": f"Please generate an email for the message: {request.message}",
            },
            ProcessMailWithAIRequestType.SUMMARY: {
                "system_prompt": "You are a mail summarizer.",
                "prompt": f"Please help summarize the email: {request.message}.",
            },
            ProcessMailWithAIRequestType.REPLY: {
                "system_prompt": "You are a mail writer.",
                "prompt": f"Please help me write a reply to the email: {request.message}",
            },
        }

        # Get the prompt based on the request type
        return prompts.get(request.request_type, prompts[ProcessMailWithAIRequestType.GENERATE])

    async def process_mail_with_ai(
        self,
        request: ProcessMailWithAIRequestBody,
    ) -> dict:
        prompt = self._generate_prompt(request)
        processed_mail = self.openai_client.get_completion(**prompt)
        return {"processed_mail": processed_mail}
