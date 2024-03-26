import { authorizedApiRequestWrapper2 } from '.';

const getMails = authorizedApiRequestWrapper2('/mails', 'get');

const getMailsByLinkedAddress = authorizedApiRequestWrapper2('/mails/mail-address/:link_mail_address/mails', 'get');

const getMail = authorizedApiRequestWrapper2('/mails/:mail_address/:mail_id', 'get');

const sendMail = authorizedApiRequestWrapper2('/mails', 'post');

const processMailWithAI = authorizedApiRequestWrapper2('/mails/process-with-ai', 'post');

const scheduleMail = authorizedApiRequestWrapper2('/schedule-mail', 'post');

export { getMails, getMail, sendMail, processMailWithAI, scheduleMail, getMailsByLinkedAddress };
