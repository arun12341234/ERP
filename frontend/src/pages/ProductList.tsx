/**
 * Product List page - Product catalog management
 */
import { useState, useEffect } from 'react';
import { api } from '../lib/api';

interface Product {
  id: number;
  sku: string;
  name: string;
  product_type: string;
  cost_price: number;
  selling_price: number;
  is_active: boolean;
}

export default function ProductList() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const data = await api.get('/products');
      setProducts(data);
    } catch (error) {
      console.error('Failed to load products:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="p-8">Loading...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Product Catalog</h1>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">SKU</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Cost Price</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Selling Price</th>
              <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Status</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {products.map((product) => (
              <tr key={product.id}>
                <td className="px-6 py-4 whitespace-nowrap font-mono text-sm">{product.sku}</td>
                <td className="px-6 py-4 whitespace-nowrap font-medium text-gray-900">{product.name}</td>
                <td className="px-6 py-4 whitespace-nowrap capitalize text-gray-600">{product.product_type.replace('_', ' ')}</td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-gray-600">${product.cost_price.toFixed(2)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-gray-600">${product.selling_price.toFixed(2)}</td>
                <td className="px-6 py-4 whitespace-nowrap text-center">
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    product.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {product.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
