import 'dotenv/config';

const XERO_TOKEN_URL = "https://identity.xero.com/connect/token";
const XERO_API_BASE = "https://api.xero.com/api.xro/2.0";

/**
 * Step 1: Get access token
 */
async function getAccessToken() {
  const body = new URLSearchParams({
    grant_type: "client_credentials",
    client_id: process.env.XERO_CLIENT_ID,
    client_secret: process.env.XERO_CLIENT_SECRET,
    scope: "accounting.transactions accounting.contacts"
  });

  const res = await fetch(XERO_TOKEN_URL, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body
  });

  if (!res.ok) throw new Error(`Token error: ${await res.text()}`);
  return res.json();
}

/**
 * Step 2: Get tenant (organisation) ID
 */
async function getTenantId(accessToken) {
  const res = await fetch("https://api.xero.com/connections", {
    headers: { Authorization: `Bearer ${accessToken}` }
  });

  if (!res.ok) throw new Error(`Connections error: ${await res.text()}`);
  const data = await res.json();
  return data[0]?.tenantId;
}

/**
 * Step 3: Fetch invoices
 */
async function getInvoices(accessToken, tenantId) {
  const res = await fetch(`${XERO_API_BASE}/Invoices`, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      "Xero-tenant-id": tenantId,
      Accept: "application/json"
    }
  });

  if (!res.ok) throw new Error(`Invoices error: ${await res.text()}`);
  return res.json();
}

export async function fetchXeroInvoices() {
  try {
    const tokenData = await getAccessToken();
    const accessToken = tokenData.access_token;

    const tenantId = await getTenantId(accessToken);
    if (!tenantId) throw new Error("No tenant ID found.");

    const invoices = await getInvoices(accessToken, tenantId);
    console.log("✅ Invoices from Xero:", JSON.stringify(invoices, null, 2));

    return invoices;
  } catch (err) {
    console.error("❌ Xero fetch failed:", err.message);
  }
}
