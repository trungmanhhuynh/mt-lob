all_stocks = ['9269', '3022', '2051', '3879', '10166', '1080', '12059', '1907', '2050', '11390', '1956', '2057', '4736',
          '2368', '4575', '2028', '11038', '1388', '2813', '9069', '3459', '9094', '2748', '2094', '4060', '9063',
          '1694', '9268', '12255', '9062', '9086', '11869', '4481', '4618', '4695', '9761', '12098', '3388', '12534',
          '12552', '2645', '11583', '9065', '9266', '2197', '11234', '7843', '2602', '9074', '12456', '3161', '12417',
          '2290', '9034', '11946', '2822', '11714', '1113', '10470', '4218', '2651', '9270', '9265', '7858', '4549',
          '1472', '1243', '4799', '5836', '12713', '1221', '3035', '1431', '10484', '1769', '9058', '11867', '10508',
          '11399', '2730', '9926', '4851', '10795', '13113', '3107', '4320', '9064', '8080', '11244', '11618', '9061',
          '10887', '1229', '12327', '13003', '3757', '2890', '4154', '1865', '13061', '9067']

cluster1 = ['9061', '3459', '4549', '9761', '4851']
cluster2 = ['9062', '11869', '12255', '2748', '4320']
cluster3 = ['11583', '4799', '9268', '10470', '9058']

chosen_stocks = cluster1 + cluster2 + cluster3

rs_params = [(0.1, 0.1), (0.1, 0.5), (0.01, 0.1), (0.01, 0.5), (0.25, 0.25)]