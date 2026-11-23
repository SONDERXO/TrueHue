package com.example.skintonecorrection.ui.home

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.skintonecorrection.ui.BrandMark
import com.example.skintonecorrection.ui.WorkflowAction

@Composable
fun HomeScreen(onPickPhoto: () -> Unit) {
    val colors = MaterialTheme.colorScheme
    Scaffold(containerColor = colors.background) { insets ->
        Box(Modifier.fillMaxSize().padding(insets), contentAlignment = Alignment.Center) {
            Column(Modifier.widthIn(max = 360.dp).fillMaxWidth().verticalScroll(rememberScrollState()).padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(12.dp)) {
                BrandMark()
                Text("TrueHue", style = MaterialTheme.typography.headlineLarge, fontWeight = FontWeight.Bold,
                    letterSpacing = (-.8).sp, textAlign = TextAlign.Center)
                Text("Adjust portrait lighting and colour, then compare with the original.",
                    style = MaterialTheme.typography.bodyLarge, color = colors.onSurfaceVariant,
                    textAlign = TextAlign.Center)
                Spacer(Modifier.height(4.dp))
                WorkflowAction("Choose photo", onPickPhoto)
                Text("Your photos stay on this device.", style = MaterialTheme.typography.bodySmall,
                    color = colors.onSurfaceVariant, textAlign = TextAlign.Center)
            }
        }
    }
}
