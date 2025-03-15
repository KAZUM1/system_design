import React from "react";
import SwaggerUI from "swagger-ui-react";
import "swagger-ui-react/swagger-ui.css";

const ui = SwaggerUIBundle({
    url: "/openapi.json",
    dom_id: "#swagger-ui",
    presets: [SwaggerUIBundle.presets.apis, SwaggerUIStandalonePreset],
    layout: "StandaloneLayout",
    deepLinking: true,
    defaultModelsExpandDepth: -1,
    theme: {
        primaryColor: "#FFD700", // Желтый цвет
        textColor: "#fff",       // Белый текст
        backgroundColor: "#222"  // Тёмный фон
    }
});

export default SwaggerDocs;
