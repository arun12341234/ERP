/**
 * Main application component with routing.
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import ProtectedRoute from './components/ProtectedRoute';
import Header from './components/Header';
import Footer from './components/Footer';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import ItemList from './pages/ItemList';
import ItemDetail from './pages/ItemDetail';
import ItemForm from './pages/ItemForm';
import LeadList from './pages/LeadList';
import CustomerList from './pages/CustomerList';
import ProductList from './pages/ProductList';

function App() {
  const { user, loading, login, logout } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Loading...</div>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col bg-gray-50">
        <Header user={user} onLogout={logout} />

        <main className="flex-grow">
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login onLogin={login} />} />
            <Route path="/register" element={<Register />} />

            {/* Protected routes */}
            <Route element={<ProtectedRoute isAuthenticated={!!user} />}>
              <Route path="/dashboard" element={<Dashboard user={user} />} />

              {/* Items (sample module) */}
              <Route path="/items" element={<ItemList />} />
              <Route path="/items/:id" element={<ItemDetail />} />
              <Route path="/items/:id/edit" element={<ItemForm />} />
              <Route path="/items/new" element={<ItemForm />} />

              {/* CRM & Sales */}
              <Route path="/leads" element={<LeadList />} />
              <Route path="/customers" element={<CustomerList />} />
              <Route path="/opportunities" element={<div className="p-8 text-center">Opportunities - Coming Soon</div>} />
              <Route path="/quotes" element={<div className="p-8 text-center">Quotes - Coming Soon</div>} />
              <Route path="/sales-orders" element={<div className="p-8 text-center">Sales Orders - Coming Soon</div>} />
              <Route path="/tickets" element={<div className="p-8 text-center">Support Tickets - Coming Soon</div>} />

              {/* Inventory & Procurement */}
              <Route path="/products" element={<ProductList />} />
              <Route path="/vendors" element={<div className="p-8 text-center">Vendors - Coming Soon</div>} />
              <Route path="/purchase-orders" element={<div className="p-8 text-center">Purchase Orders - Coming Soon</div>} />
            </Route>

            {/* Catch all */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>

        <Footer />
      </div>
    </BrowserRouter>
  );
}

export default App;
