document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('fertilizer-form');
    const resultsDiv = document.getElementById('results');

    form.addEventListener('submit', function (event) {
        event.preventDefault();

        const plantType = document.getElementById('plant-type').value;
        const areaSize = parseFloat(document.getElementById('area-size').value);

        if (!plantType || isNaN(areaSize) || areaSize <= 0) {
            resultsDiv.innerHTML = '<p>Please enter valid values for plant type and area size.</p>';
            return;
        }

        // Define recommended fertilizer rates (kg per hectare)
        const fertilizerRates = {
            tomato: { dap: 150, mop: 100, urea: 200 },
            corn: { dap: 200, mop: 150, urea: 250 },
            rose: { dap: 120, mop: 90, urea: 180 },
            wheat: { dap: 160, mop: 110, urea: 220 },
            carrot: { dap: 140, mop: 100, urea: 190 },
            lettuce: { dap: 130, mop: 80, urea: 170 },
            cucumber: { dap: 140, mop: 90, urea: 200 },
            pepper: { dap: 150, mop: 100, urea: 210 },
            spinach: { dap: 120, mop: 85, urea: 175 },
            potato: { dap: 160, mop: 110, urea: 230 },
            onion: { dap: 150, mop: 95, urea: 200 },
            garlic: { dap: 140, mop: 90, urea: 190 },
            bean: { dap: 130, mop: 85, urea: 180 },
            cabbage: { dap: 140, mop: 90, urea: 190 },
            cauliflower: { dap: 130, mop: 85, urea: 180 },
            broccoli: { dap: 120, mop: 80, urea: 170 },
            eggplant: { dap: 140, mop: 95, urea: 200 },
            squash: { dap: 130, mop: 85, urea: 180 },
            pumpkin: { dap: 140, mop: 90, urea: 190 },
            zucchini: { dap: 130, mop: 85, urea: 180 },
            strawberry: { dap: 120, mop: 80, urea: 170 },
            blueberry: { dap: 110, mop: 70, urea: 150 },
            raspberry: { dap: 120, mop: 75, urea: 160 },
            blackberry: { dap: 120, mop: 75, urea: 160 },
            grape: { dap: 140, mop: 90, urea: 200 },
            apple: { dap: 150, mop: 100, urea: 210 },
            pear: { dap: 140, mop: 90, urea: 200 },
            peach: { dap: 150, mop: 100, urea: 210 },
            plum: { dap: 140, mop: 90, urea: 200 },
            cherry: { dap: 150, mop: 100, urea: 210 },
            apricot: { dap: 140, mop: 90, urea: 200 },
            fig: { dap: 130, mop: 85, urea: 190 },
            pomegranate: { dap: 140, mop: 90, urea: 200 },
            kiwi: { dap: 130, mop: 85, urea: 190 }
        };

        // Conversion factor from hectares to square meters
        const hectareToSqM = 10000;

        // Get the recommended rates for the selected plant
        const rates = fertilizerRates[plantType];

        if (!rates) {
            resultsDiv.innerHTML = '<p>Recommended rates for the selected plant are not available.</p>';
            return;
        }

        // Calculate the amount of fertilizer needed
        const dapNeeded = (rates.dap * areaSize) / hectareToSqM;
        const mopNeeded = (rates.mop * areaSize) / hectareToSqM;
        const ureaNeeded = (rates.urea * areaSize) / hectareToSqM;

        // Display the results
        resultsDiv.innerHTML = `
            <h2>Recommended Fertilizer Amounts</h2>
            <p><strong>DAP:</strong> ${dapNeeded.toFixed(2)} kg</p>
            <p><strong>MOP:</strong> ${mopNeeded.toFixed(2)} kg</p>
            <p><strong>Urea:</strong> ${ureaNeeded.toFixed(2)} kg</p>
        `;
    });
});
