package com.example.skintonecorrection.ui.result

import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import coil.compose.AsyncImage
import com.example.skintonecorrection.ui.SharedViewModel

@Composable
fun ResultScreen(sharedViewModel:SharedViewModel,onReSelect:()->Unit){
    val state by sharedViewModel.uiState.collectAsStateWithLifecycle()
    var message by remember{mutableStateOf("")}
    var showTrial by remember{mutableStateOf(false)}
    var showMask by remember{mutableStateOf(false)}
    val imageExport=rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("image/png")){destination ->
        val source=state.correctedImageUri
        if(destination!=null && source!=null)sharedViewModel.export(source,destination){message=it}
        else if(destination==null)message="Save cancelled. Your result is unchanged."
    }
    val reportExport=rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/json")){destination ->
        val source=state.reportUri
        if(destination!=null && source!=null)sharedViewModel.export(source,destination){message=it}
        else if(destination==null)message="Save cancelled. Your result is unchanged."
    }
    Scaffold { padding ->
        Column(Modifier.fillMaxSize().padding(padding).verticalScroll(rememberScrollState()).padding(24.dp),verticalArrangement=Arrangement.spacedBy(12.dp)) {
            Text("Compare your result",style=MaterialTheme.typography.headlineSmall)
            Text("Research prototype · experimental correction",style=MaterialTheme.typography.labelLarge)
            Card(Modifier.fillMaxWidth()) {
                Column(Modifier.padding(16.dp),verticalArrangement=Arrangement.spacedBy(8.dp)) {
                    Text(if(showTrial) "Trial correction" else "Before correction",style=MaterialTheme.typography.titleMedium)
                    val comparisonUri=if(showTrial)state.correctedImageUri else state.photoUsedUri
                    if(comparisonUri!=null)AsyncImage(model=comparisonUri,contentDescription=if(showTrial) "Trial correction" else "Photo before correction",modifier=Modifier.fillMaxWidth().height(280.dp),contentScale=ContentScale.Fit)
                    Row(Modifier.fillMaxWidth(),horizontalArrangement=Arrangement.spacedBy(8.dp)) {
                        FilterChip(selected=!showTrial,onClick={showTrial=false},label={Text("Before")})
                        FilterChip(selected=showTrial,onClick={showTrial=true},label={Text("Trial correction")})
                    }
                    Text("Both views use the same 256 × 256 working image.",style=MaterialTheme.typography.bodySmall)
                }
            }
            OutlinedButton(onClick={showMask=!showMask},modifier=Modifier.fillMaxWidth()){Text(if(showMask) "Hide selected skin" else "Inspect selected skin")}
            if(showMask){
                Text("White pixels show where this prototype selected skin. Check for missing skin or unwanted areas before judging the correction.")
                if(state.maskUri!=null)AsyncImage(model=state.maskUri,contentDescription="Selected skin mask: white indicates selected pixels",modifier=Modifier.fillMaxWidth().height(256.dp),contentScale=ContentScale.Fit)
            }
            Text("This build uses the older correction model, which failed research quality checks. Skin-tone estimates and correction quality are unvalidated. Newer masking remains in Python development.",style=MaterialTheme.typography.bodySmall)
            Text("Your original is unchanged. Processing stays on this phone; files leave the app only when you choose a save destination.",style=MaterialTheme.typography.bodySmall)
            if(message.isNotEmpty())Text(message)
            Button(onClick={imageExport.launch("truehue_experimental.png")},enabled=state.correctedImageUri!=null,modifier=Modifier.fillMaxWidth()){Text("Save trial image")}
            OutlinedButton(onClick={reportExport.launch("truehue_report.json")},enabled=state.reportUri!=null,modifier=Modifier.fillMaxWidth()){Text("Save report")}
            OutlinedButton(onClick=onReSelect,modifier=Modifier.fillMaxWidth()){Text("Choose another photo")}
        }
    }
}
