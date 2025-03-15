import React from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import FileManager from "./FileManager";
import SwaggerDocs from "./SwaggerUI";

const App = () => {
  return (
    <Router>
      <div>
        <nav style={{ padding: "10px", backgroundColor: "#333" }}>
          <Link to="/" style={{ color: "#ffcc00", marginRight: "15px" }}>Мега-Диск</Link>
          <Link to="/docs" style={{ color: "#ffcc00" }}>API</Link>
        </nav>
        <Routes>
          <Route path="/" element={<FileManager />} />
          <Route path="/docs" element={<SwaggerDocs />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
