package com.example.skintonecorrection.ui.home

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.example.skintonecorrection.ui.BrandMark
import com.example.skintonecorrection.ui.InfoPanel
import com.example.skintonecorrection.ui.WorkflowAction
import com.example.skintonecorrection.ui.WorkflowPage

@Composable
fun HomeScreen(onPickPhoto: () -> Unit) {
    WorkflowPage(actions = { WorkflowAction("Select photo from gallery", onPickPhoto) }) {
        Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            BrandMark()
            Column {
                Text("TrueHue", style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
                Text("On-device portrait correction", style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }
        Text("Correct facial exposure and colour in a portrait. Compare the result with the original before saving.",
            color = MaterialTheme.colorScheme.onSurfaceVariant)
        InfoPanel("Private by design", "Your photos are processed on your phone.")
        Column(verticalArrangement = Arrangement.spacedBy(13.dp)) {
            Text("How it works", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            val steps = listOf(
                "Choose a portrait" to "Use a clear photo of one person.",
                "Apply correction" to "TrueHue finds the face and adjusts exposure and colour.",
                "Compare and save" to "Review the difference, then save a full-size copy."
            )
            steps.forEachIndexed { index, (title, detail) ->
                Row(horizontalArrangement = Arrangement.spacedBy(11.dp)) {
                    Surface(shape = CircleShape, color = MaterialTheme.colorScheme.primary,
                        contentColor = MaterialTheme.colorScheme.onPrimary) {
                        Box(Modifier.size(25.dp), contentAlignment = Alignment.Center) {
                            Text((index + 1).toString(), style = MaterialTheme.typography.labelSmall)
                        }
                    }
                    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
                        Text(title, style = MaterialTheme.typography.titleSmall)
                        Text(detail, style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                }
            }
        }
    }
}
