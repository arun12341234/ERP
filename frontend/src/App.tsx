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
import LeadForm from './pages/LeadForm';
import CustomerList from './pages/CustomerList';
import CustomerForm from './pages/CustomerForm';
import CustomerDetail from './pages/CustomerDetail';
import OpportunityList from './pages/OpportunityList';
import OpportunityForm from './pages/OpportunityForm';
import OpportunityDetail from './pages/OpportunityDetail';
import ProductList from './pages/ProductList';
import WorkOrderList from './pages/WorkOrderList';
import MachineList from './pages/MachineList';
import InvoiceList from './pages/InvoiceList';
import ChartOfAccountsList from './pages/ChartOfAccountsList';
import LogisticsDashboard from './pages/LogisticsDashboard';
import ShipmentList from './pages/ShipmentList';
import WebsiteProductList from './pages/WebsiteProductList';
import OnlineOrderList from './pages/OnlineOrderList';
import SystemHealthDashboard from './pages/SystemHealthDashboard';
import AlertList from './pages/AlertList';
import RoleAssignmentList from './pages/RoleAssignmentList';

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
              <Route path="/leads/new" element={<LeadForm />} />
              <Route path="/leads/:id/edit" element={<LeadForm />} />
              <Route path="/customers" element={<CustomerList />} />
              <Route path="/customers/new" element={<CustomerForm />} />
              <Route path="/customers/:id" element={<CustomerDetail />} />
              <Route path="/customers/:id/edit" element={<CustomerForm />} />
              <Route path="/opportunities" element={<OpportunityList />} />
              <Route path="/opportunities/new" element={<OpportunityForm />} />
              <Route path="/opportunities/:id" element={<OpportunityDetail />} />
              <Route path="/opportunities/:id/edit" element={<OpportunityForm />} />
              <Route path="/quotes" element={<div className="p-8 text-center">Quotes - Coming Soon</div>} />
              <Route path="/sales-orders" element={<div className="p-8 text-center">Sales Orders - Coming Soon</div>} />
              <Route path="/tickets" element={<div className="p-8 text-center">Support Tickets - Coming Soon</div>} />

              {/* Inventory & Procurement */}
              <Route path="/products" element={<ProductList />} />
              <Route path="/vendors" element={<div className="p-8 text-center">Vendors - Coming Soon</div>} />
              <Route path="/purchase-orders" element={<div className="p-8 text-center">Purchase Orders - Coming Soon</div>} />

              {/* Manufacturing & Production */}
              <Route path="/work-orders" element={<WorkOrderList />} />
              <Route path="/machines" element={<MachineList />} />

              {/* Finance & Accounting */}
              <Route path="/invoices" element={<InvoiceList />} />
              <Route path="/chart-of-accounts" element={<ChartOfAccountsList />} />

              {/* Supply Chain & Logistics */}
              <Route path="/logistics" element={<LogisticsDashboard />} />
              <Route path="/logistics/shipments" element={<ShipmentList />} />
              <Route path="/logistics/requests" element={<div className="p-8 text-center">Logistics Requests - Coming Soon</div>} />
              <Route path="/logistics/tracking" element={<div className="p-8 text-center">Real-Time Tracking - Coming Soon</div>} />
              <Route path="/logistics/returns" element={<div className="p-8 text-center">Returns Management - Coming Soon</div>} />
              <Route path="/logistics/customs" element={<div className="p-8 text-center">Customs Documents - Coming Soon</div>} />
              <Route path="/logistics/carrier-performance" element={<div className="p-8 text-center">Carrier Performance - Coming Soon</div>} />
              <Route path="/logistics/warehouse-slots" element={<div className="p-8 text-center">Warehouse Slotting - Coming Soon</div>} />
              <Route path="/logistics/cold-chain" element={<div className="p-8 text-center">Cold Chain Monitoring - Coming Soon</div>} />

              {/* Omni-Channel Commerce & Digital Engagement */}
              <Route path="/commerce/products" element={<WebsiteProductList />} />
              <Route path="/commerce/orders" element={<OnlineOrderList />} />
              <Route path="/commerce/wallets" element={<div className="p-8 text-center">Customer Wallets - Coming Soon</div>} />
              <Route path="/commerce/returns" element={<div className="p-8 text-center">Online Returns - Coming Soon</div>} />
              <Route path="/commerce/loyalty" element={<div className="p-8 text-center">Loyalty Program - Coming Soon</div>} />
              <Route path="/commerce/campaigns" element={<div className="p-8 text-center">Offer Campaigns - Coming Soon</div>} />
              <Route path="/commerce/marketplace" element={<div className="p-8 text-center">Marketplace Sync - Coming Soon</div>} />
              <Route path="/commerce/chatbot" element={<div className="p-8 text-center">Chatbot Interactions - Coming Soon</div>} />
              <Route path="/commerce/forum" element={<div className="p-8 text-center">Community Forum - Coming Soon</div>} />
              <Route path="/commerce/reviews" element={<div className="p-8 text-center">Customer Reviews - Coming Soon</div>} />

              {/* Governance, Audit, AI & System Ops */}
              <Route path="/governance/roles" element={<RoleAssignmentList />} />
              <Route path="/governance/backups" element={<div className="p-8 text-center">Data Backups - Coming Soon</div>} />
              <Route path="/governance/health" element={<SystemHealthDashboard />} />
              <Route path="/governance/integrations" element={<div className="p-8 text-center">API Integrations - Coming Soon</div>} />
              <Route path="/governance/documents" element={<div className="p-8 text-center">Document Digitization - Coming Soon</div>} />
              <Route path="/governance/analytics" element={<div className="p-8 text-center">Analytics Dashboards - Coming Soon</div>} />
              <Route path="/governance/risks" element={<div className="p-8 text-center">Risk Assessment - Coming Soon</div>} />
              <Route path="/governance/alerts" element={<AlertList />} />
              <Route path="/governance/audit" element={<div className="p-8 text-center">Audit Trail - Coming Soon</div>} />
              <Route path="/governance/compliance" element={<div className="p-8 text-center">Regulatory Compliance - Coming Soon</div>} />
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
