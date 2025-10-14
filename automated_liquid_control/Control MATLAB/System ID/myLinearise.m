function G = myLinearise(BlockData)
[x, u] = findop(BlockData.Parameters.Value, 'snapshot', 2, ones(1000,1));
G = linearize(BlockData.Parameters.Value, u, x);
end