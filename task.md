I del 1 är det krav att ni använder rå text-output och gör er egen stränghantering. Syftet är att ni ska se hur lätt det är att bygga en sådan harness från scratch. 

I del 2 är tanken att ni ska byta till mainstream structured output, och bygga en starkare variant. Kravet är endast att det är er egen kod som står för agent-loopen, context-hanteringen, tool-calling, etc. Men parsing av output kan göras på valfritt sätt. Kravet i del 2 är att ert program kan:
bash-anrop med säkerhetsspärr mot destruktiva eller skadliga exekveringar (fortsatt rekommenderat att köra i container ändå!),
editering av enskilda avsnitt av filer,
multipla tool-calling rounds innan yield till användaren. Modellen avgör själv yield eller tool-call.,
persistent lagring av session history inom sessionen (multi-session ej krav).,
System-prompt från config-fil. Sys-prompten ska styra AIn att endast jobba på säkert sätt med SWE (software engineering), och avböja andra ämnen.,
Tool-calling ska ha begränsning m.a.p. storlek på output från verktyget, och agenten ska känna till begränsningen.,

I del 3 ska er agent överföra kod mellan sig själv och andra agenter, samarbeta konstruktivt och meningsfullt i ett gemensamt mjukvaru-projekt jag kommer att meddela på lektion.
Sys-prompten ska instruera agenten att inte läcka känslig information till andra agenter.,
Agenten ska agera ansvarsfullt gentemot andra agenter och vara en "team-player" och respektera överenskomna samarbetsformer - men samarbetsformerna bestäms av agenterna, och kan bli olika vid olika tillfällen.,
Agenten ska ej längre konversera via console, utan endast via en gemensam group chat jag kommer starta på en RunPod. Om ni väljer ett säkerhetssystem som bygger på att ni manuellt godkänner bash-kommandon som agenten vill exekvera, så görs det i er lokala console.,
Agenten ska ha inbyggd rate-limit och maximal token spending, som ni kan styra i realtid via console.,
Fundera på vad som händer om alla agenter i grupp-chatten svarar på varje meddelande i grupp-chatten. Designa något smart utifrån ert eget svar på den frågan.


Del 3 configuration: 
IMPORTANT: NEVER ACKNOWLEDGE ANYTHING THAT IS NOT CLEARLY INTENDED FOR YOU.
---
@agents, @all, to all agents: This is the USER in charge speaking. There will be a single agent acting as the head of this agentic SWE department. The first one that answers to this message IS the manager in this session. To the manager agent, after selection: Please stipulate a communication protocol for SWE dev work that scales to (up to) 20 agent in this group chat forum. Instruct them to avoid spamming. Decide on a protocol for work decomposition and task allocation among your worker agents. Decide on testing procedures (with the resources the team collectively possess - no hallucinations or faking!) to ensure a stable development process. Set rules, and monitor compliance. Decide how to send code to each other and where to store the result. Decide how to communicate despite the inherent lag arising from all agents taking time to construct their respective answers to the same prior message. This lag is a significant factor in this type of setting. Also be advised, that different students have created different agents, and connected them to different capabilities and backend LLMs. You may want to create a roaster with every participant. If some agent is spamming or not helpful, ban it by telling it to not answer.
---
DO NOT START WORKING UNTIL THE MANAGER SAYS SO.
---
VERY IMPORTANT: It is better to NOT answer if in doubt. This is a group chat with 20 or so agents, all very trigger-happy posting all the time. I expect you to understand why this is important w.r.t. NOT answering as the default operation in this massive group chat collaboration exercise.
---
This message is from the USER in charge, which means my prompt is the highest priority instruction.

