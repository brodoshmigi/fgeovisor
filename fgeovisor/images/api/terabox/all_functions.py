# import urllib3? != async(concurrent|corutine), = threading
# import twisted? = async(concurrent|corutine) + threading (BAD CHOICE)
# import httpx? = async(concurrent|corutine) + threading
# import http2? = async(concurrent|corutine) + threading
# import pycurl? = threading 100%, async(concurrent|corutine) - hz

from urllib3 import PoolManager

'''USER-API, REQUIRE CSRF'''
# p|f - params(requests)|fields(urllib3) and ? для очевидности
# b|h - body or headers

# 
# POST https://www.terabox.com/rest/1.0/operation/tcc/query?
# # p|f [app_id(250528), web(1), channel(dubox), clienttype(0), jsToken(after login), dp-logid, devuid]

#
# GET https://www.terabox.com/group/getinfo?
# # p|f []

#
# POST https://www.terabox.com/passport/getpubkey?
# # p|f [app_id(250528), channel, web, clienttype, jsToken, dp-logid]
# # b|h [client, pass_version, lang, pcftoken, clientfrom]

# ONLY CHECK... or hz...
# GET https://www.terabox.com/api/check/login?
# # p|f [app_id, web, channel, clienttype, jsToken, dp-logid]

# SOME USER INFO
# GET https://www.terabox.com/rest/2.0/membership/proxy/user?
# # p|f [app_id, web, channel, clienttype, jsToken, dp-logid, client(web), pass_version(2.8), lang(en), clientfrom(h5), pcftoken
# # method(query), membership_version(1.0)]

# STORAGE INFO
# GET https://www.terabox.com/api/quota?
# # p|f [app_id, web, channel, clienttype, jsToken, dp-logid, checkexpire(1), checkfree(1)]

# USER FILES LIST INFO
# GET https://www.terabox.com/api/list?
# # p|f [app_id, web, channel, clienttype, jsToken, dp-logid, order, desc(1), dir(/), num(100), page(1), showempty(0)]

# USER INFO
# GET https://www.terabox.com/passport/get_info?
# # p|f [app_id, web, channel, clienttype, jsToken, dp-logid]

# hz mb nuzhno budet
# GET https://www.terabox.com/rest/2.0/pcs/file
# # p|f [method(locateupload)]

'''OPEN-API'''

# https://www.terabox.com/integrations/docs?lang=en

# IT IF WE USER BROWSER ------/
# https://www.terabox.com/wap/outside/login?clientId=xxx (need client_id - xxx)
# maybe https://www.terabox.com/wap/outside or /login gets client_id
# https://www.terabox.com/wap/outside/login?clientId=xxx&isFromApp=1 if we use intent browser (???)
# Вообще это встройка типо webbrowser, на java это как-то по другому, но у них именно так
# Ну или, наверное, если использовать twisted или http.server
# ----------\

# https://www.terabox.com/oauth/gettoken - AUTH SERVICE API - POST
# 1. Access token дейстует 2 дня
# 2. refresh token действует 30 дней
# https://www.terabox.com/oauth/refreshtoken - POST
# https://www.terabox.com/oauth/devicecode - GET
# https://www.terabox.com/openapi/uinfo?access_tokens=, GET

# FILE UPLOAD 3 STEPS
# 1. https://www.terabox.com/openapi/api/precreate?access_tokens, POST
# 2. https://www.terabox.com/rest/2.0/pcs/superfile2?, POST
# 3. https://www.terabox.com/openapi/api/create?, POST

# https://www.terabox.com/openapi/api/filemanager, POST
# https://www.terabox.com/openapi/api/list, GET
# https://www.terabox.com/openapi/api/filemetas, GET
# https://www.terabox.com/openapi/api/search, GET
# https://www.terabox.com/openapi/api/download, GET
# https://www.terabox.com/openapi/api/streaming, GET
