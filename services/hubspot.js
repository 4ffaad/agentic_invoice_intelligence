import fetch from "node-fetch";

const urlDeals =
  "https://api.hubapi.com/crm/v3/objects/deals?properties=dealname,amount,closedate,dealstage,pipeline,createdate";

export async function getDeals() {
  const response = await fetch(urlDeals, {
    headers: {
      Authorization: `Bearer ${process.env.HUBSPOT_ACCESS_TOKEN}`,
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`HubSpot API error ${response.status}: ${await response.text()}`);
  }

  const data = await response.json();
  return data.results || [];
}
