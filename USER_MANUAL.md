# 🛍️ Achol Fashion Store: Operation Manual

Welcome to the **Achol Fashion Store** platform. This guide provides step-by-step instructions for managing your online boutique, handling customer orders, and maintaining the technical health of the site.

---

## 🔐 1. Accessing the Management Portal

Industry-standard security has been implemented to protect your store from automated bots and unauthorized access.

### The Secret Path
The administrative interface is hidden at a custom URL:
**[https://achol-fashion-store.onrender.com/management/](https://achol-fashion-store.onrender.com/management/)**

### Staff Abstraction (Security)
*   **Customer View**: If a regular user or a bot tries to visit `/management/`, they will see a **404 Page Not Found**. This makes it appear as though the portal doesn't exist.
*   **Easy Access**: As an Admin, once you log in with your credentials on the main site, a **"Management Portal"** link will automatically appear in the top navigation bar and footer.

---

## 📦 2. Product Management

Your products are the heart of the store. Here is how to manage them:

1.  **Categories**: Organize your stock (e.g., "Men", "Women", "Accessories").
2.  **Adding a Product**: 
    *   Navigate to **Products > Add Product**.
    *   **Images**: Upload photos directly. They are automatically processed and stored securely on **Cloudinary**.
    *   **Slug**: This is the URL name (e.g., `silk-red-dress`). It is usually auto-generated from the name.
3.  **Pricing**: Ensure you set the correct price and currency.

---

## 🛒 3. Order Processing

When a customer makes a purchase, it moves through your workflow:

1.  **New Orders**: Check the **Orders** section frequently.
2.  **Status Updates**:
    *   `Pending`: Order received but not yet processed.
    *   `Processing`: You are currently preparing the shipment.
    *   `Shipped`: The item is on its way to the customer.
    *   `Completed`: The customer has received the item.
3.  **Email Notifications**: The system handles basic logging; you can monitor details in the Admin dashboard.

---

## 🛠️ 4. Technical Overview (Modern Stack)

Achol Fashion Store is built with a high-end, scalable architecture:

*   **Backend**: Django 4.2 (Secure, Scalable Python Framework).
*   **Frontend**: Vanilla CSS + Tailwind CSS (Fast, Mobile-responsive UI).
*   **Database**: PostgreSQL (Hosted on Neon).
*   **Media/Images**: **Cloudinary** (Professional-grade image transformation and storage).
*   **Build System**: Optimized **WhiteNoise** with custom resilient storage to ensure zero downtime during updates.
*   **Hosting**: Render (Web Services).

---

## 🆘 5. Troubleshooting & Support

> [!TIP]
> **Build Errors?** We use a custom `ResilientWhiteNoiseStorage` class in `production.py`. This ensures your site doesn't crash even if third-party CSS files have broken internal links.

> [!IMPORTANT]
> **Environment Variables**: If you change passwords or API keys, ensure they are updated in the **Render Dashboard > Environment** section.

---

*&copy; 2026 Achol Fashion Store. Designed for excellence.*
