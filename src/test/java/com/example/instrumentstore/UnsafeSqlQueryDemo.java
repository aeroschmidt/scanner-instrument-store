package com.example.instrumentstore;

import jakarta.servlet.http.HttpServletRequest;
import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

/**
 * Intentionally vulnerable, test-only fixture for the CodeQL demonstration.
 * It is not wired into an application route and must not be copied into production code.
 */
final class UnsafeSqlQueryDemo {

    private UnsafeSqlQueryDemo() {
    }

    static ResultSet searchByName(HttpServletRequest request, Connection connection) throws SQLException {
        String name = request.getParameter("name");
        Statement statement = connection.createStatement();
        String query = "SELECT id, name FROM products WHERE name = '" + name + "'";
        return statement.executeQuery(query);
    }
}
